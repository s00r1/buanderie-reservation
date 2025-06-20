# Buanderie Reservation

This application manages online reservations for a laundry's machines. It is written in Python using the Flask microframework. An instance is available at [https://soury.pythonanywhere.com](https://soury.pythonanywhere.com/).

- [Version française](README.md)
- [النسخة العربية](README.ar.md)

## Installation

Make sure you have Python installed, then install the dependencies:

```bash
pip install -r requirements.txt
```

## Running locally

Execute the `app.py` file directly to start the local server:

```bash
python app.py
```

The application will then be available at [http://localhost:5000](http://localhost:5000).

## Configuration variables

Two environment variables allow you to adjust the application's behavior:

- `RESERVATIONS_FILE`: path to the JSON file used to store reservations. By default, `reservations.json` in the project root is used.
- `ADMIN_CODE`: secret code that allows deleting any reservation. The default value is `s00r1`.

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
