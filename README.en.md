# Buanderie Reservation

This application manages online reservations for a laundry's machines. It is written in Python using the Flask microframework. An instance is available at [https://soury.pythonanywhere.com](https://soury.pythonanywhere.com/).

- [Version française](README.md)
- [النسخة العربية](README.ar.md)

## Table of contents
- [Installation](#installation)
- [Running locally](#running-locally)
- [Configuration](#configuration)
- [Data management](#data-management)
- [User guide](#user-guide)
- [Deploying on NanoPi Neo (or equivalents)](#deploying-on-nanopi-neo-or-equivalents)
- [Deploying on PythonAnywhere](#deploying-on-pythonanywhere)
- [Tests](#tests)
- [Contributing](#contributing)
- [License](#license)

## Installation

Ensure that **Python 3** and `git` are available on your machine.

1. Download or clone this repository.
2. *(Optional)* Create a virtual environment:

   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. Install the dependencies:

   ```bash
   pip install -r requirements.txt
   ```

## Running locally

Execute the `app.py` file directly to start the local server:

```bash
python app.py
```

The application will then be available at [http://localhost:5000](http://localhost:5000).

## Configuration

Two environment variables control the application's behaviour:

- `RESERVATIONS_FILE` – path to the JSON file storing reservations. By default it is `reservations.json` at the repository root.
- `ADMIN_CODE` – secret code that allows deleting any reservation. Default is `s00r1`.

## Data management

Reservations are kept in the file specified by `RESERVATIONS_FILE`. To start with a blank database, create this file containing only:

```json
[]
```

The application locks the file while writing to avoid corruption.

The JSON file lives on the server hosting the application (e.g.
[PythonAnywhere](https://www.pythonanywhere.com/)). Every visitor shares this
file, so any reservation created or removed becomes immediately visible to other
users.

## User guide

### Making a reservation

1. Select your **room**.
2. Pick the **date** and **start time**.
3. Choose the **machine**.
4. Specify the **number of cycles** (1–3).
5. Enter a **4-digit code** and confirm.

Rules:
- the code must contain exactly four digits;
- a single machine cannot exceed **3 cycles per day**;
- the slot must end **before 11 p.m.**

### Cancelling

Click the booking in the calendar and enter the same code to confirm deletion.

## Deploying on NanoPi Neo (or equivalents)

This guide explains a full installation on a small ARM board (NanoPi Neo, Raspberry Pi, etc.) running a **Debian/Armbian**-based system.

### 1. Prepare the board

- Update the system and install the required tools:

  ```bash
  sudo apt update
  sudo apt install -y python3 python3-venv python3-pip git
  ```

### 2. Get the application

- Clone this repository and enter the directory:

  ```bash
  git clone https://github.com/your-user/buanderie-reservation.git
  cd buanderie-reservation
  ```

- *(Optional)* Create a virtual environment and install the dependencies:

  ```bash
  python3 -m venv venv
  source venv/bin/activate
  pip install -r requirements.txt
  ```

### 3. Configure the application

Set the following environment variables (adapt them to your setup):

```bash
export RESERVATIONS_FILE=/home/pi/buanderie-reservation/reservations.json
export ADMIN_CODE=your_secret_code
```

### 4. Start the server

- For a quick test (port 5000):

  ```bash
  python app.py
  ```

- For a more robust network service (port 8080):

  ```bash
  gunicorn app:app --bind 0.0.0.0:8080
  ```

### 5. Make the service persistent *(optional)*

To restart the application automatically, create a `systemd` service:

```bash
sudo nano /etc/systemd/system/buanderie.service
```

Minimal content of the file:

```ini
[Unit]
Description=Buanderie Reservation
After=network.target

[Service]
WorkingDirectory=/home/pi/buanderie-reservation
ExecStart=/usr/bin/python3 /home/pi/buanderie-reservation/app.py
Environment="RESERVATIONS_FILE=/home/pi/buanderie-reservation/reservations.json"
Environment="ADMIN_CODE=your_secret_code"
Restart=always

[Install]
WantedBy=multi-user.target
```

Then enable the service:

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now buanderie.service
```

The application is now accessible at `http://<board_ip>:5000` (or on the port used by `gunicorn`).

### 6. Simplifying access for users

To offer a friendlier URL than `http://<board_ip>:5000`, you can assign a local hostname and redirect traffic to port 80:

1. **Rename the machine to "buanderie"**

   Edit `/etc/hosts`:

   ```bash
   sudo nano /etc/hosts
   ```

   Replace the line that looks like:

   ```text
   127.0.1.1    old-name
   ```

   with:

   ```text
   127.0.1.1    buanderie
   ```

2. **Enable mDNS resolution**

   Install and start *Avahi* to access `buanderie.local` from your network:

   ```bash
   sudo apt install avahi-daemon
   sudo systemctl enable avahi-daemon
   sudo systemctl start avahi-daemon
   ```

3. **Redirect port 80 to 5000**

   To avoid typing the port in the browser, redirect port 80 to the port 5000 used by Flask:

   ```bash
   sudo iptables -t nat -A PREROUTING -p tcp --dport 80 -j REDIRECT --to-port 5000

   # Save the rule so it survives reboots
   sudo sh -c "iptables-save > /etc/iptables.rules"

   # Reload rules automatically at startup
   sudo sh -c 'echo -e "#!/bin/sh\niptables-restore < /etc/iptables.rules" > /etc/network/if-pre-up.d/iptables'
   sudo chmod +x /etc/network/if-pre-up.d/iptables
   ```

After these steps, the application is reachable at `http://buanderie.local` without specifying a port.

## Deploying on PythonAnywhere

1. Create an account on [pythonanywhere.com](https://www.pythonanywhere.com/) and open a Bash console.
2. Clone the project and enter the directory:

   ```bash
   git clone https://github.com/your-user/buanderie-reservation.git
   cd buanderie-reservation
   ```

3. Create a virtual environment and install the dependencies:

   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

4. From the **Web** tab, create a new *Manual configuration* application and point it to this folder.
5. Edit the WSGI file to expose the Flask app:

   ```python
   import sys
   sys.path.insert(0, '/home/<user>/buanderie-reservation')
   from app import app as application
   ```

6. In the *Environment Variables* section, set `RESERVATIONS_FILE` and `ADMIN_CODE` (e.g. `RESERVATIONS_FILE=/home/<user>/buanderie-reservation/reservations.json`).
7. Finally click **Reload** to start the application.

## Running in production

PythonAnywhere runs the application with **Gunicorn**. The provided `Procfile`
launches the server with:

```bash
gunicorn app:app --bind 0.0.0.0:${PORT:-8080}
```

The port is handled automatically by the platform. You can reuse this command to
test locally or on any compatible host.

## Tests

A suite of unit tests verifies the main routes of the application. After installing the dependencies, simply run:

```bash
pytest
```

## Contributing

Contributions are welcome! Open an issue to discuss a change or propose a pull request. Be sure to run `pytest` before submitting.

---

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.
