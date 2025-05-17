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

    reservations.append({
        "title": f"Chambre {data['chambre']}",
        "start": start,
        "end": end,
        "machine": data['machine']
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

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)