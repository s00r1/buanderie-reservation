
from flask import Flask, request, jsonify, render_template
import json
import logging

logging.basicConfig(level=logging.INFO)

app = Flask(__name__, template_folder="templates", static_folder="static")
DATA_FILE = "reservations.json"

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/reserver", methods=["POST"])
def reserver():
    data = request.get_json()
    try:
        with open(DATA_FILE, "r") as f:
            reservations = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        logging.warning("Could not load reservations: %s", e)
        reservations = []

    start = f"{data['date']}T{data['heure']}"
    end_hour = int(data['heure'].split(":")[0]) + int(data['tournees'])
    end = f"{data['date']}T{str(end_hour).zfill(2)}:00"

    for r in reservations:
        if r["machine"] == data["machine"] and r["start"] == start:
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

    reservations.append({
        "title": f"Chambre {data['chambre']}",
        "start": start,
        "end": end,
        "machine": data["machine"],
        "code": data["code"]
    })

    with open(DATA_FILE, "w") as f:
        json.dump(reservations, f)

    return jsonify({"status": "ok"})

@app.route("/get_reservations", methods=["GET"])
def get_reservations():
    try:
        with open(DATA_FILE, "r") as f:
            reservations = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        logging.warning("Could not load reservations: %s", e)
        reservations = []
    return jsonify(reservations)

@app.route("/delete_reservation", methods=["POST"])
def delete_reservation():
    data = request.get_json()
    try:
        with open(DATA_FILE, "r") as f:
            reservations = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        logging.warning("Could not load reservations: %s", e)
        reservations = []

    updated = []
    deleted = False
    for r in reservations:
        if r["start"].startswith(data["start"][:16]):
            if data["code"] == "s0r1" or r.get("code") == data["code"]:
                deleted = True
                continue
        updated.append(r)

    if deleted:
        with open(DATA_FILE, "w") as f:
            json.dump(updated, f)
        return jsonify({"status": "deleted"})
    else:
        return jsonify({"status": "error", "message": "❌ Code incorrect ou réservation introuvable."}), 403

if __name__ == "__main__":
    app.run(debug=True)
