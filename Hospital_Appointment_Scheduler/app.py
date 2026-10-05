from __future__ import annotations

import base64
from contextlib import contextmanager
import hmac
import json
import logging
import os
import re
import sqlite3
from collections.abc import Iterator
from datetime import date
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

ROOT = Path(__file__).resolve().parent
STATIC_DIR = ROOT / "static"
SLOTS = (
    "09:00", "09:30", "10:00", "10:30", "11:00", "11:30",
    "13:00", "13:30", "14:00", "14:30", "15:00", "15:30",
    "16:00", "16:30",
)
DOCTORS = (
    ("dr-olivia-chen", "Dr. Olivia Chen", "Family Medicine"),
    ("dr-marcus-reed", "Dr. Marcus Reed", "Cardiology"),
    ("dr-priya-shah", "Dr. Priya Shah", "Pediatrics"),
    ("dr-james-wilson", "Dr. James Wilson", "Dermatology"),
)
EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
PHONE_PATTERN = re.compile(r"^[+()0-9 .-]{7,30}$")


class RequestError(Exception):
    def __init__(self, status: int, message: str) -> None:
        super().__init__(message)
        self.status = status


class SlotUnavailable(Exception):
    pass


def database_path() -> Path:
    configured = os.environ.get("APPOINTMENT_DB_PATH", "data/appointments.sqlite3")
    path = Path(configured)
    return path if path.is_absolute() else ROOT / path


@contextmanager
def connect(db_path: Path) -> Iterator[sqlite3.Connection]:
    connection = sqlite3.connect(db_path, timeout=10)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    try:
        with connection:
            yield connection
    finally:
        connection.close()


def initialize_database(db_path: Path) -> None:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    with connect(db_path) as connection:
        connection.execute("PRAGMA journal_mode = WAL")
        connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS doctors (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                specialty TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS appointments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                doctor_id TEXT NOT NULL REFERENCES doctors(id),
                appointment_date TEXT NOT NULL,
                appointment_time TEXT NOT NULL,
                patient_name TEXT NOT NULL,
                patient_email TEXT NOT NULL,
                patient_phone TEXT NOT NULL DEFAULT '',
                created_at TEXT NOT NULL DEFAULT (datetime('now')),
                UNIQUE (doctor_id, appointment_date, appointment_time)
            );
            """
        )
        connection.executemany(
            "INSERT OR IGNORE INTO doctors (id, name, specialty) VALUES (?, ?, ?)",
            DOCTORS,
        )


def parse_appointment(payload: object) -> dict[str, str]:
    if not isinstance(payload, dict):
        raise RequestError(400, "Send appointment details as a JSON object.")

    doctor_id = payload.get("doctor_id")
    appointment_date = payload.get("date")
    appointment_time = payload.get("time")
    patient_name = payload.get("patient_name")
    patient_email = payload.get("patient_email")
    patient_phone = payload.get("patient_phone", "")

    if not all(isinstance(value, str) for value in (
        doctor_id, appointment_date, appointment_time,
        patient_name, patient_email, patient_phone,
    )):
        raise RequestError(400, "Complete each required appointment field.")
    if doctor_id not in {doctor[0] for doctor in DOCTORS}:
        raise RequestError(400, "Choose a listed doctor.")
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", appointment_date):
        raise RequestError(400, "Choose a valid appointment date.")
    try:
        parsed_date = date.fromisoformat(appointment_date)
    except ValueError as exc:
        raise RequestError(400, "Choose a valid appointment date.") from exc
    if parsed_date < date.today():
        raise RequestError(400, "Appointments cannot be booked in the past.")
    if appointment_time not in SLOTS:
        raise RequestError(400, "Choose a listed appointment time.")

    patient_name = patient_name.strip()
    patient_email = patient_email.strip()
    patient_phone = patient_phone.strip()
    if not patient_name or len(patient_name) > 100:
        raise RequestError(400, "Enter a name of up to 100 characters.")
    if len(patient_email) > 254 or not EMAIL_PATTERN.fullmatch(patient_email):
        raise RequestError(400, "Enter a valid email address.")
    if patient_phone and not PHONE_PATTERN.fullmatch(patient_phone):
        raise RequestError(400, "Enter a valid phone number or leave it blank.")

    return {
        "doctor_id": doctor_id,
        "date": appointment_date,
        "time": appointment_time,
        "patient_name": patient_name,
        "patient_email": patient_email,
        "patient_phone": patient_phone,
    }


def create_appointment(db_path: Path, appointment: dict[str, str]) -> dict[str, object]:
    with connect(db_path) as connection:
        cursor = connection.execute(
            """
            INSERT INTO appointments (
                doctor_id, appointment_date, appointment_time,
                patient_name, patient_email, patient_phone
            ) VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT (doctor_id, appointment_date, appointment_time) DO NOTHING
            """,
            (
                appointment["doctor_id"], appointment["date"],
                appointment["time"], appointment["patient_name"],
                appointment["patient_email"], appointment["patient_phone"],
            ),
        )
        if cursor.rowcount == 0:
            raise SlotUnavailable
        row = connection.execute(
            """
            SELECT a.id, a.appointment_date AS date, a.appointment_time AS time,
                   a.patient_name, a.patient_email, a.patient_phone,
                   d.id AS doctor_id, d.name AS doctor_name, d.specialty
            FROM appointments a JOIN doctors d ON d.id = a.doctor_id
            WHERE a.id = ?
            """,
            (cursor.lastrowid,),
        ).fetchone()
    return dict(row)


def create_handler(db_path: Path, username: str, password: str) -> type[BaseHTTPRequestHandler]:
    expected_auth = "Basic " + base64.b64encode(
        f"{username}:{password}".encode("utf-8")
    ).decode("ascii")

    class Handler(BaseHTTPRequestHandler):
        server_version = "ClinicAppointments"

        def end_headers(self) -> None:
            self.send_header("X-Content-Type-Options", "nosniff")
            self.send_header("Referrer-Policy", "no-referrer")
            self.send_header("X-Frame-Options", "DENY")
            self.send_header("Cache-Control", "no-store")
            self.send_header(
                "Content-Security-Policy",
                "default-src 'self'; style-src 'self'; script-src 'self'; "
                "connect-src 'self'; base-uri 'none'; frame-ancestors 'none'; "
                "form-action 'self'",
            )
            super().end_headers()

        def respond_json(self, status: int, payload: object) -> None:
            body = json.dumps(payload).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def authenticate(self) -> bool:
            supplied = self.headers.get("Authorization", "")
            if hmac.compare_digest(supplied, expected_auth):
                return True
            self.send_response(401)
            self.send_header("WWW-Authenticate", 'Basic realm="Clinic appointments"')
            self.send_header("Content-Length", "0")
            self.end_headers()
            return False

        def read_json(self) -> object:
            content_type = self.headers.get("Content-Type", "").split(";", 1)[0].strip()
            if content_type != "application/json":
                raise RequestError(415, "Use Content-Type: application/json.")
            content_length = self.headers.get("Content-Length", "")
            if not content_length.isdigit() or int(content_length) > 8192:
                raise RequestError(400, "The request body is missing or too large.")
            try:
                return json.loads(self.rfile.read(int(content_length)))
            except (json.JSONDecodeError, UnicodeDecodeError) as exc:
                raise RequestError(400, "Send valid JSON.") from exc

        def do_GET(self) -> None:
            if not self.authenticate():
                return
            path = urlsplit(self.path).path
            if path == "/api/doctors":
                with connect(db_path) as connection:
                    rows = connection.execute(
                        "SELECT id, name, specialty FROM doctors ORDER BY name"
                    ).fetchall()
                self.respond_json(200, [dict(row) for row in rows])
            elif path == "/api/slots":
                self.respond_json(200, list(SLOTS))
            elif path == "/api/appointments":
                query = parse_qs(urlsplit(self.path).query)
                appointment_date = query.get("date", [date.today().isoformat()])[0]
                try:
                    parsed_date = date.fromisoformat(appointment_date)
                    if parsed_date.isoformat() != appointment_date:
                        raise ValueError
                except ValueError:
                    self.respond_json(400, {"error": "Choose a valid appointment date."})
                    return
                with connect(db_path) as connection:
                    rows = connection.execute(
                        """
                        SELECT a.id, a.appointment_date AS date,
                               a.appointment_time AS time, a.patient_name,
                               a.patient_email, a.patient_phone,
                               d.id AS doctor_id, d.name AS doctor_name,
                               d.specialty
                        FROM appointments a JOIN doctors d ON d.id = a.doctor_id
                        WHERE a.appointment_date = ?
                        ORDER BY a.appointment_time, d.name
                        """,
                        (appointment_date,),
                    ).fetchall()
                self.respond_json(200, [dict(row) for row in rows])
            elif path == "/" or path in ("/static/app.js", "/static/styles.css"):
                filename = "index.html" if path == "/" else path.rsplit("/", 1)[-1]
                content_type = "text/html; charset=utf-8" if filename.endswith(".html") else (
                    "text/javascript; charset=utf-8" if filename.endswith(".js")
                    else "text/css; charset=utf-8"
                )
                body = (STATIC_DIR / filename).read_bytes()
                self.send_response(200)
                self.send_header("Content-Type", content_type)
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
            else:
                self.respond_json(404, {"error": "Not found."})

        def do_POST(self) -> None:
            if not self.authenticate():
                return
            if urlsplit(self.path).path != "/api/appointments":
                self.respond_json(404, {"error": "Not found."})
                return
            try:
                appointment = parse_appointment(self.read_json())
                created = create_appointment(db_path, appointment)
            except RequestError as exc:
                self.respond_json(exc.status, {"error": str(exc)})
            except SlotUnavailable:
                self.respond_json(
                    409,
                    {"error": "That appointment slot was just booked. Choose another time."},
                )
            else:
                self.respond_json(201, created)

        def do_DELETE(self) -> None:
            if not self.authenticate():
                return
            match = re.fullmatch(r"/api/appointments/(\d+)", urlsplit(self.path).path)
            if not match:
                self.respond_json(404, {"error": "Not found."})
                return
            with connect(db_path) as connection:
                cursor = connection.execute(
                    "DELETE FROM appointments WHERE id = ?", (int(match.group(1)),)
                )
            if cursor.rowcount == 0:
                self.respond_json(404, {"error": "Appointment not found."})
                return
            self.send_response(204)
            self.send_header("Content-Length", "0")
            self.end_headers()

        def log_message(self, format: str, *args: object) -> None:
            logging.info("%s - %s", self.address_string(), format % args)

    return Handler


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    username = os.environ.get("APPOINTMENT_APP_USER", "staff")
    password = os.environ.get("APPOINTMENT_APP_PASSWORD", "")
    if len(password) < 16:
        raise SystemExit(
            "Set APPOINTMENT_APP_PASSWORD to a unique password of at least 16 characters."
        )
    db_path = database_path()
    initialize_database(db_path)
    host = os.environ.get("APPOINTMENT_HOST", "127.0.0.1")
    port = int(os.environ.get("APPOINTMENT_PORT", "8000"))
    server = ThreadingHTTPServer((host, port), create_handler(db_path, username, password))
    logging.info("Serving on http://%s:%d", host, port)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        logging.info("Shutting down")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()