
from flask import Flask, request, jsonify, render_template
import json
import os

app = Flask(__name__)
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
    except:
        reservations = []

    start = f"{data['date']}T{data['heure']}"
    end_hour = int(data['heure'].split(':')[0]) + int(data['tournees'])
    end = f"{data['date']}T{str(end_hour).zfill(2)}:00"

    # Vérifie si créneau déjà pris pour la même machine
    for r in reservations:
        if r['machine'] == data['machine']:
            if not (end <= r['start'] or start >= r['end']):
                return jsonify({"status": "conflict", "message": "Créneau déjà réservé"}), 409

    reservations.append({
        "title": f"Chambre {data['chambre']}",
        "start": start,
        "end": end,
        "machine": data['machine'],
        "code": data['code']
    })

    with open(DATA_FILE, "w") as f:
        json.dump(reservations, f)

    return jsonify({"status": "ok"})

@app.route("/get_reservations", methods=["GET"])
def get_reservations():
    try:
        with open(DATA_FILE, "r") as f:
            reservations = json.load(f)
    except:
        reservations = []
    return jsonify(reservations)

@app.route("/delete_reservation", methods=["POST"])
def delete_reservation():
    data = request.get_json()
    try:
        with open(DATA_FILE, "r") as f:
            reservations = json.load(f)
    except:
        reservations = []

    found = False
    updated_reservations = []
    for r in reservations:
        if r["start"] == data["start"]:
            if r["code"] == data["code"] or data["code"] == "s0r1":
                found = True
                continue
        updated_reservations.append(r)

    with open(DATA_FILE, "w") as f:
        json.dump(updated_reservations, f)

    if found:
        return jsonify({"status": "deleted"}), 200
    else:
        return jsonify({"status": "unauthorized"}), 403

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
