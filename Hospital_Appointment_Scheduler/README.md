# Carewell appointment desk

A small, self-hosted clinic scheduling demo. It includes a responsive staff
dashboard, appointment booking and cancellation, a SQLite database, and an
EC2 deployment example.

> **Demo only:** Do not enter real patient or health information. This starter
> is not a production-ready or HIPAA-compliant medical system. Before any real
> use, have qualified security and compliance professionals review the system;
> add individual staff accounts, least-privilege access, audit logging,
> retention and deletion policies, encrypted storage and backups, monitoring,
> incident response, and an appropriate AWS/organizational compliance program.

## Run locally

Requires Python 3.10 or newer; no third-party packages are needed.

In PowerShell:

```powershell
$env:APPOINTMENT_APP_PASSWORD = "local-demo-password-change-me"
python app.py
```

Open <http://127.0.0.1:8000>. The browser will prompt for HTTP Basic
Authentication; the username is `staff` unless `APPOINTMENT_APP_USER` is set.
Choose a unique password of at least 16 characters. For a different local
database location, set `APPOINTMENT_DB_PATH`.

The database creates four fictional demo doctors on first startup. Each doctor
has fourteen bookable half-hour slots on weekdays-style clinic hours. A doctor
and time slot can only be booked once on a given date; cancellation makes the
slot available again.

## Run tests

```powershell
python -m unittest discover -s tests -v
```

## Deploy on an Ubuntu EC2 instance

This example runs the Python application on localhost and terminates TLS at
Nginx. Use an Ubuntu LTS AMI. Point a DNS name you control (for example,
`appointments.example.com`) at the instance before requesting a TLS
certificate.

1. Create an EC2 security group that permits inbound TCP **22 only from your
   admin IP** and TCP **80 and 443** for web traffic. Do not expose port 8000.
   Use an IAM instance role only if the deployment needs AWS services. Keep the
   operating system and packages patched.
2. Connect to the instance, install Nginx and Certbot, and create the
   application and database directories:

   ```bash
   sudo apt update
   sudo apt install -y python3 nginx certbot python3-certbot-nginx
   sudo install -d -o root -g www-data -m 0750 /opt/hospital-appointments
   sudo install -d -o www-data -g www-data -m 0700 /var/lib/hospital-appointments
   ```

3. Copy this project to `/opt/hospital-appointments` (for example, via a
   private Git checkout or SCP). Set ownership so only administrators can
   change the code:

   ```bash
   sudo chown -R root:www-data /opt/hospital-appointments
   sudo chmod -R o-rwx /opt/hospital-appointments
   ```

4. Create `/etc/hospital-appointments.env` with a **unique** strong password
   (at least 16 characters); do not put secrets in the repository:

   ```bash
   sudo sh -c 'umask 027; printf "APPOINTMENT_APP_USER=staff\nAPPOINTMENT_APP_PASSWORD=%s\n" "$(openssl rand -base64 32)" > /etc/hospital-appointments.env'
   sudo chown root:www-data /etc/hospital-appointments.env
   sudo chmod 0640 /etc/hospital-appointments.env
   ```

   Store the generated password in your approved password manager. If rotating
   it later, edit this file and restart the service. Basic Authentication is
   only suitable here behind HTTPS; the application itself binds to localhost.

5. First start Nginx with a temporary HTTP-only site for your domain, then
   obtain a certificate. Replace `appointments.example.com` with your DNS
   name:

   ```bash
   sudo tee /etc/nginx/sites-available/hospital-appointments >/dev/null <<'EOF'
   server {
       listen 80;
       server_name appointments.example.com;
       location / { return 404; }
   }
   EOF
   sudo ln -s /etc/nginx/sites-available/hospital-appointments /etc/nginx/sites-enabled/hospital-appointments
   sudo nginx -t && sudo systemctl reload nginx
   sudo certbot --nginx -d appointments.example.com
   ```

6. Replace every `appointments.example.com` in the included Nginx
   configuration with your DNS name. Install the systemd service and Nginx
   TLS configuration:

   ```bash
   sudo install -m 0644 /opt/hospital-appointments/deploy/hospital-appointments.service /etc/systemd/system/hospital-appointments.service
   sudo cp /opt/hospital-appointments/deploy/nginx.conf /etc/nginx/sites-available/hospital-appointments
   sudo nginx -t
   sudo systemctl daemon-reload
   sudo systemctl enable --now hospital-appointments
   sudo systemctl reload nginx
   ```

   Check `sudo systemctl status hospital-appointments` and
   `sudo journalctl -u hospital-appointments -n 50`. Open your HTTPS domain and
   sign in with the configured username and password.

7. Plan and test encrypted backups of `/var/lib/hospital-appointments` and
   restoration before relying on the database. Restrict who can access the EC2
   instance and backups. SQLite on one instance is intended only for a small
   demo, not a multi-instance or production medical workload.

## Application endpoints

- `GET /api/doctors` and `GET /api/slots` return the demo booking options.
- `GET /api/appointments?date=YYYY-MM-DD` lists that day's appointments.
- `POST /api/appointments` books a slot using JSON appointment details.
- `DELETE /api/appointments/{id}` cancels an appointment.

Every route requires the configured Basic Authentication credentials. The
database enforces one booking per doctor, date, and time slot, including
simultaneous booking attempts.
