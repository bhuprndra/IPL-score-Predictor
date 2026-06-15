from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import pickle
import joblib
import pandas as pd
import os

app = Flask(__name__)
CORS(app)

# LOAD MODEL
MODEL_PATH = os.path.join(os.path.dirname(__file__), "model.joblib")

try:
    with open(MODEL_PATH, "rb") as f:
        model =joblib.load(f)
    print("✅ Model loaded successfully")
except Exception as e:
    model = None
    print("❌ Error loading model:", e)

# TEAMS
TEAMS = [
    "Chennai Super Kings",
    "Delhi Capitals",
    "Gujarat Titans",
    "Kolkata Knight Riders",
    "Lucknow Super Giants",
    "Mumbai Indians",
    "Punjab Kings",
    "Rajasthan Royals",
    "Royal Challengers Bangalore",
    "Sunrisers Hyderabad"
]

# CITIES
VENUES = ["Bangalore", "Chandigarh", "Delhi", "Mumbai", "Kolkata", "Jaipur", "Hyderabad",
          "Chennai", "Cape Town", "Port Elizabeth", "Durban", "Centurion", "East London",
          "Johannesburg", "Kimberley", "Bloemfontein", "Ahmedabad", "Cuttack", "Nagpur", 
          "Dharamsala", "Visakhapatnam", "Pune", "Raipur", "Ranchi", "Abu Dhabi", "Sharjah", 
          "Dubai", "Indore", "Bengaluru", "Navi Mumbai", "Lucknow"
]

# PREDICTION FUNCTION
def predict_score(data):

    batting_team = data["batting_team"]
    bowling_team = data["bowling_team"]
    venue = data["venue"]

    overs = float(data["overs"])
    runs = int(data["runs"])
    wickets = int(data["wickets"])

    runs_last5 = int(data["runs_last5"])
    wickets_last5 = int(data["wickets_last5"])

    if model is None:
        raise Exception("Model not loaded")

    features = pd.DataFrame({
        "batting_team": [batting_team],
        "bowling_team": [bowling_team],
        "city": [venue],
        "current_score": [runs],
        "overs": [overs],
        "wickets": [wickets],
        "runs_last_5": [runs_last5],
        "wickets_last_5": [wickets_last5]
    })

    predicted = int(round(float(model.predict(features)[0])))

    lower = max(0, predicted - 10)
    upper = predicted + 10

    return {
        "predicted_score": predicted,
        "score_range": f"{lower}-{upper}",
        "lower": lower,
        "upper": upper
    }

# ROUTES
@app.route("/")
def home():
    print("VENUES:", VENUES)
    return render_template(
        "index.html",
        teams=TEAMS,
        venues=VENUES
    )

@app.route("/api/options")
def options():
    return jsonify({
        "teams": TEAMS,
        "venues": VENUES
    })

@app.route("/api/predict", methods=["POST"])
def predict():

    try:

        data = request.get_json(force=True)

        required_fields = [
            "batting_team",
            "bowling_team",
            "venue",
            "overs",
            "runs",
            "wickets",
            "runs_last5",
            "wickets_last5"
        ]

        for field in required_fields:
            if field not in data:
                return jsonify({
                    "error": f"Missing field: {field}"
                }), 400

        if data["batting_team"] == data["bowling_team"]:
            return jsonify({
                "error": "Batting team and Bowling team cannot be same"
            }), 400

        result = predict_score(data)

        return jsonify(result)

    except Exception as e:
        return jsonify({
            "error": str(e)
        }), 500

# MAIN
if __name__ == "__main__":
    app.run(debug=True)