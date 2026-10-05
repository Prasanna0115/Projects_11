import base64
from concurrent.futures import ThreadPoolExecutor
import json
import tempfile
import threading
import unittest
from datetime import date, timedelta
from http.server import ThreadingHTTPServer
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from app import create_handler, initialize_database


class AppointmentApiTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = Path(self.temp_dir.name) / "appointments.sqlite3"
        initialize_database(self.db_path)
        self.server = ThreadingHTTPServer(
            ("127.0.0.1", 0), create_handler(self.db_path, "staff", "test-password-long")
        )
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.base_url = f"http://127.0.0.1:{self.server.server_port}"
        token = base64.b64encode(b"staff:test-password-long").decode("ascii")
        self.headers = {"Authorization": f"Basic {token}"}

    def tearDown(self):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=2)
        self.temp_dir.cleanup()

    def request(
        self, path, *, method="GET", payload=None, raw_body=None,
        content_type="application/json", authenticated=True,
    ):
        headers = dict(self.headers) if authenticated else {}
        body = raw_body
        if payload is not None:
            body = json.dumps(payload).encode("utf-8")
        if body is not None and content_type:
            headers["Content-Type"] = content_type
        request = Request(f"{self.base_url}{path}", data=body, headers=headers, method=method)
        try:
            with urlopen(request) as response:
                content = response.read()
                return response.status, self.decode_response(response, content)
        except HTTPError as error:
            content = error.read()
            return error.code, self.decode_response(error, content)

    @staticmethod
    def decode_response(response, content):
        if not content:
            return None
        if response.headers.get_content_type() == "application/json":
            return json.loads(content)
        return content.decode("utf-8")

    def booking(self, **overrides):
        return {
            "doctor_id": "dr-olivia-chen",
            "date": (date.today() + timedelta(days=1)).isoformat(),
            "time": "09:00",
            "patient_name": "Alex Morgan",
            "patient_email": "alex@example.com",
            "patient_phone": "",
            **overrides,
        }

    def test_appointment_data_requires_authentication(self):
        for path, method in (
            ("/", "GET"),
            ("/static/app.js", "GET"),
            ("/api/doctors", "GET"),
            ("/api/slots", "GET"),
            ("/api/appointments", "GET"),
            ("/api/appointments", "POST"),
            ("/api/appointments/1", "DELETE"),
        ):
            with self.subTest(path=path, method=method):
                status, _ = self.request(path, method=method, authenticated=False)
                self.assertEqual(status, 401)

    def test_booking_appears_in_daily_schedule(self):
        appointment = self.booking()
        status, created = self.request("/api/appointments", method="POST", payload=appointment)
        self.assertEqual(status, 201)
        self.assertEqual(created["patient_name"], "Alex Morgan")
        status, schedule = self.request(f"/api/appointments?date={appointment['date']}")
        self.assertEqual(status, 200)
        self.assertEqual(len(schedule), 1)
        self.assertEqual(schedule[0]["doctor_name"], "Dr. Olivia Chen")

    def test_doctor_cannot_be_double_booked_in_a_time_slot(self):
        appointment = self.booking()
        self.assertEqual(
            self.request("/api/appointments", method="POST", payload=appointment)[0], 201
        )
        status, response = self.request(
            "/api/appointments", method="POST", payload=self.booking(patient_name="Jordan Lee")
        )
        self.assertEqual(status, 409)
        self.assertIn("just booked", response["error"])

    def test_simultaneous_bookings_only_create_one_appointment(self):
        def book(name):
            return self.request(
                "/api/appointments",
                method="POST",
                payload=self.booking(patient_name=name),
            )[0]

        with ThreadPoolExecutor(max_workers=2) as executor:
            statuses = list(executor.map(book, ("Alex Morgan", "Jordan Lee")))

        self.assertCountEqual(statuses, [201, 409])

    def test_invalid_booking_inputs_are_rejected(self):
        invalid_bookings = (
            {"doctor_id": "unknown-doctor"},
            {"date": "2099-02-30"},
            {"time": "08:00"},
            {"patient_name": "   "},
            {"patient_email": "not-an-email"},
            {"patient_phone": "not a phone number"},
        )
        for invalid_fields in invalid_bookings:
            with self.subTest(invalid_fields=invalid_fields):
                status, _ = self.request(
                    "/api/appointments",
                    method="POST",
                    payload=self.booking(**invalid_fields),
                )
                self.assertEqual(status, 400)

    def test_post_requires_json_and_rejects_malformed_json(self):
        status, _ = self.request(
            "/api/appointments",
            method="POST",
            payload=self.booking(),
            content_type="text/plain",
        )
        self.assertEqual(status, 415)

        status, _ = self.request(
            "/api/appointments",
            method="POST",
            raw_body=b'{"date": ',
        )
        self.assertEqual(status, 400)

    def test_schedule_rejects_invalid_date_and_unknown_paths(self):
        status, _ = self.request("/api/appointments?date=2099-02-30")
        self.assertEqual(status, 400)
        status, _ = self.request("/api/not-found")
        self.assertEqual(status, 404)

    def test_past_date_is_rejected(self):
        status, response = self.request(
            "/api/appointments",
            method="POST",
            payload=self.booking(date="2000-01-01"),
        )
        self.assertEqual(status, 400)
        self.assertIn("past", response["error"])

    def test_cancellation_removes_appointment(self):
        status, created = self.request(
            "/api/appointments", method="POST", payload=self.booking()
        )
        self.assertEqual(status, 201)
        status, _ = self.request(f"/api/appointments/{created['id']}", method="DELETE")
        self.assertEqual(status, 204)
        status, schedule = self.request(f"/api/appointments?date={created['date']}")
        self.assertEqual(status, 200)
        self.assertEqual(schedule, [])

    def test_cancelling_unknown_appointment_returns_not_found(self):
        status, response = self.request("/api/appointments/999999", method="DELETE")
        self.assertEqual(status, 404)
        self.assertEqual(response["error"], "Appointment not found.")

    def test_frontend_assets_are_served_with_security_headers(self):
        request = Request(
            f"{self.base_url}/static/app.js",
            headers=self.headers,
        )
        with urlopen(request) as response:
            self.assertEqual(response.status, 200)
            self.assertEqual(response.headers.get_content_type(), "text/javascript")
            self.assertIn("Content-Security-Policy", response.headers)
            self.assertEqual(response.headers["X-Content-Type-Options"], "nosniff")
            self.assertIn("function renderAppointments", response.read().decode("utf-8"))

if __name__ == "__main__":
    unittest.main()
