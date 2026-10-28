from flask import Flask, jsonify, request

app = Flask(__name__)

# Program data carried over from the original desktop (Tkinter) versions
PROGRAMS = {
    "FL": {
        "name": "Fat Loss",
        "workout": [
            "Mon: 5x5 Back Squat + AMRAP",
            "Tue: EMOM 20min Assault Bike",
            "Wed: Bench Press + 21-15-9",
            "Thu: 10RFT Deadlifts/Box Jumps",
            "Fri: 30min Active Recovery",
        ],
        "diet": ["B: 3 Egg Whites + Oats Idli", "L: Grilled Chicken + Brown Rice", "D: Fish Curry + Millet Roti"],
        "calories_per_kg": 24,
    },
    "MG": {
        "name": "Muscle Gain",
        "workout": [
            "Mon: Squat 5x5",
            "Tue: Bench 5x5",
            "Wed: Deadlift 4x6",
            "Thu: Front Squat 4x8",
            "Fri: Incline Press 4x10",
            "Sat: Barbell Rows 4x10",
        ],
        "diet": ["B: 4 Eggs + PB Oats", "L: Chicken Biryani (250g Chicken)", "D: Mutton Curry + Jeera Rice"],
        "calories_per_kg": 35,
    },
    "BG": {
        "name": "Beginner",
        "workout": ["Circuit Training: Air Squats, Ring Rows, Push-ups", "Focus: technique and form"],
        "diet": ["Balanced Tamil meals: Idli-Sambar, Rice-Dal, Chapati", "Protein: 120g/day"],
        "calories_per_kg": 30,
    },
}

clients = {}
_next_id = 1


def calc_bmi(weight_kg, height_cm):
    if weight_kg <= 0 or height_cm <= 0:
        raise ValueError("weight and height must be positive")
    h = height_cm / 100
    return round(weight_kg / (h * h), 1)


def calc_calories(program, weight_kg):
    if program not in PROGRAMS:
        raise KeyError(program)
    return int(PROGRAMS[program]["calories_per_kg"] * weight_kg)


def _error(msg, code=400):
    return jsonify({"error": msg}), code


@app.route("/")
def index():
    return jsonify({"app": "ACEest Fitness & Gym", "status": "running"})


@app.route("/health")
def health():
    return jsonify({"status": "ok"})


@app.route("/programs")
def list_programs():
    return jsonify({code: p["name"] for code, p in PROGRAMS.items()})


@app.route("/programs/<code>")
def get_program(code):
    program = PROGRAMS.get(code.upper())
    if program is None:
        return _error("program not found", 404)
    return jsonify(program)


@app.route("/clients", methods=["GET"])
def list_clients():
    return jsonify(list(clients.values()))


@app.route("/clients", methods=["POST"])
def add_client():
    global _next_id
    data = request.get_json(silent=True) or {}
    name = str(data.get("name", "")).strip()
    program = str(data.get("program", "")).upper()
    if not name:
        return _error("name is required")
    if program not in PROGRAMS:
        return _error("invalid program")
    try:
        weight = float(data.get("weight"))
        height = float(data.get("height"))
        bmi = calc_bmi(weight, height)
    except (TypeError, ValueError):
        return _error("weight and height must be positive numbers")

    client = {
        "id": _next_id,
        "name": name,
        "program": program,
        "weight": weight,
        "height": height,
        "bmi": bmi,
        "calories": calc_calories(program, weight),
    }
    clients[_next_id] = client
    _next_id += 1
    return jsonify(client), 201


@app.route("/clients/<int:client_id>", methods=["GET"])
def get_client(client_id):
    client = clients.get(client_id)
    if client is None:
        return _error("client not found", 404)
    return jsonify(client)


@app.route("/clients/<int:client_id>", methods=["DELETE"])
def delete_client(client_id):
    if clients.pop(client_id, None) is None:
        return _error("client not found", 404)
    return "", 204


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
