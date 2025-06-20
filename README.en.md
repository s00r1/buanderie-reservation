# Buanderie Reservation

This application manages online reservations for a laundry's machines. It is written in Python using the Flask microframework. An instance is available at [https://soury.pythonanywhere.com](https://soury.pythonanywhere.com/).

- [Version française](README.md)
- [النسخة العربية](README.ar.md)

## Table of contents
- [Installation](#installation)
- [Running locally](#running-locally)
- [Configuration](#configuration)
- [Data management](#data-management)
- [Deploying on PythonAnywhere](#deploying-on-pythonanywhere)
- [Tests](#tests)
- [Contributing](#contributing)
- [License](#license)

## Installation

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

For a production environment, it is recommended to use Gunicorn and bind the application to the port provided by the platform. This works the same on Fly.io, Railway or any host setting the `PORT` variable:

```bash
gunicorn app:app --bind 0.0.0.0:${PORT:-8080}
```

The included `Procfile` uses this command to simplify deployment on various platforms.

## Tests

A suite of unit tests verifies the main routes of the application. After installing the dependencies, simply run:

```bash
pytest
```

## Contributing

Contributions are welcome! Open an issue to discuss a change or propose a pull request. Be sure to run `pytest` before submitting.

---

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.
