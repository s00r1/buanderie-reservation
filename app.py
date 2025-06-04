
from flask import Flask, request, jsonify, render_template, make_response
import json
import logging
import os
import re
from datetime import datetime
from fpdf import FPDF
from filelock import FileLock

logging.basicConfig(level=logging.INFO)

app = Flask(__name__, template_folder="templates", static_folder="static")
# Allow overriding the reservations storage path via an environment variable
# Default to 'reservations.json' if not set
DATA_FILE = os.getenv("RESERVATIONS_FILE", "reservations.json")
ADMIN_CODE = os.getenv("ADMIN_CODE", "s00r1")
CODE_REGEX = re.compile(r"^\d{4}$")
LOCK_FILE = DATA_FILE + ".lock"


def load_reservations():
    try:
        with FileLock(LOCK_FILE):
            with open(DATA_FILE, "r") as f:
                return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        logging.warning("Could not load reservations: %s", e)
        return []


def save_reservations(reservations):
    with FileLock(LOCK_FILE):
        with open(DATA_FILE, "w") as f:
            json.dump(reservations, f)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/reserver", methods=["POST"])
def reserver():
    data = request.get_json()
    code = str(data.get("code", ""))
    if code != ADMIN_CODE and not CODE_REGEX.fullmatch(code):
        return jsonify({"status": "error", "message": "❌ Format de code invalide."}), 400
    reservations = load_reservations()

    start = f"{data['date']}T{data['heure']}"
    end_hour = int(data['heure'].split(":")[0]) + int(data['tournees'])
    end = f"{data['date']}T{str(end_hour).zfill(2)}:00"

    new_start = datetime.fromisoformat(start)
    new_end = datetime.fromisoformat(end)

    for r in reservations:
        if r["machine"] != data["machine"]:
            continue
        existing_start = datetime.fromisoformat(r["start"])
        existing_end = datetime.fromisoformat(r["end"])
        if new_start < existing_end and new_end > existing_start:
            return jsonify({"status": "error", "message": "❌ Ce créneau est déjà réservé pour cette machine."}), 409

    total_journalier = sum(
        int(r["end"].split("T")[1].split(":")[0]) - int(r["start"].split("T")[1].split(":")[0])
        for r in reservations
        if r["machine"] == data["machine"]
        and r["title"] == f"Chambre {data['chambre']}"
        and r["start"].startswith(data["date"])
    )
    if total_journalier + int(data["tournees"]) > 3:
        return jsonify({"status": "error", "message": "❌ Limite de 3 tournées par machine et par jour atteinte."}), 400

    reservation_record = {
        "title": f"Chambre {data['chambre']}",
        "start": start,
        "end": end,
        "machine": data["machine"],
        "code": data["code"],
        "created": datetime.now().strftime("%Y-%m-%d %H:%M"),
    }
    reservations.append(reservation_record)

    save_reservations(reservations)

    new_id = len(reservations) - 1

    response_payload = {
        "status": "ok",
        "reservation": {
            "chambre": data["chambre"],
            "date": data["date"],
            "start": start,
            "end": end,
            "machine": data["machine"],
            "code": data["code"],
            "id": new_id,
            "created": reservation_record["created"],
        }
    }

    return jsonify(response_payload)

@app.route("/get_reservations", methods=["GET"])
def get_reservations():
    reservations = load_reservations()
    sanitized = [
        {k: v for k, v in r.items() if k != "code"}
        for r in reservations
    ]
    return jsonify(sanitized)

@app.route("/delete_reservation", methods=["POST"])
def delete_reservation():
    data = request.get_json()
    code = str(data.get("code", ""))
    if code != ADMIN_CODE and not CODE_REGEX.fullmatch(code):
        return jsonify({"status": "error", "message": "❌ Format de code invalide."}), 400
    reservations = load_reservations()

    updated = []
    deleted = False
    for r in reservations:
        if r["start"].startswith(data["start"][:16]):
            if data["code"] == ADMIN_CODE or r.get("code") == data["code"]:
                deleted = True
                continue
        updated.append(r)

    if deleted:
        save_reservations(updated)
        return jsonify({"status": "deleted"})
    else:
        return jsonify({"status": "error", "message": "❌ Code incorrect ou réservation introuvable."}), 403


@app.route("/receipt/<int:res_id>")
def receipt(res_id: int):
    reservations = load_reservations()
    if res_id < 0 or res_id >= len(reservations):
        return "Reservation not found", 404
    r = reservations[res_id]
    created_str = r.get("created")
    created_dt = datetime.fromisoformat(created_str) if created_str else None
    if request.args.get("pdf") == "1":
        pdf = FPDF(unit="mm", format=(80, 120))
        pdf.add_page()
        pdf.set_font("Arial", "B", 14)
        pdf.cell(0, 8, "Reçu de réservation", ln=True, align="C")
        pdf.ln(2)
        pdf.set_font("Arial", "", 11)
        pdf.cell(0, 6, r["title"], ln=True)
        pdf.cell(0, 6, f"Machine : {r['machine']}", ln=True)
        pdf.cell(0, 6, f"Début : {r['start'].replace('T', ' ')}", ln=True)
        pdf.cell(0, 6, f"Fin : {r['end'].replace('T', ' ')}", ln=True)
        pdf.cell(0, 6, f"Code : {r['code']}", ln=True)
        pdf.ln(4)
        pdf.set_font("Arial", "I", 8)
        if created_dt:
            footer_text = f"Hotel Grill - réservation effectuée le {created_dt.strftime('%Y-%m-%d %H:%M')}"
        else:
            footer_text = "Hotel Grill"
        pdf.cell(0, 5, footer_text, ln=True, align="C")
        response = make_response(pdf.output(dest="S").encode("latin-1"))
        response.headers["Content-Type"] = "application/pdf"
        response.headers["Content-Disposition"] = "attachment; filename=receipt.pdf"
        return response

    return render_template(
        "receipt.html",
        reservation=r,
        hotel_name="Hotel Grill",
        generated=datetime.now(),
        created=created_dt,
    )

if __name__ == "__main__":
    app.run(debug=True)
