# IPL Score Predictor 🏏

A full-stack web application that predicts IPL match scores using your own Machine Learning model.

---

## Project Structure

```
ipl-predictor/
├── app.py              ← Flask backend + prediction logic
├── requirements.txt    ← Python dependencies
├── model.joblib           ← YOUR trained ML model (drop it here)
├── static/
│   └── css/
│       └──style.cs
│   └──js
│       └──script.js
├── templates/
│   └── index.html      ← Frontend UI
└── README.md
```

---

## Setup Instructions

### 1. Install dependencies

```bash
cd ipl-predictor
pip install -r requirements.txt
```

### 2. Add your trained model

Copy your trained scikit-learn (or any pickle-compatible) model to this folder:

```bash
cp /path/to/your/model.pkl ./model.pkl
```

### 3. Update `app.py` to match your model

Open `app.py` and find the `predict_score()` function. Update:

**a) Feature vector** — match the exact column order your model was trained on:

```python
features = np.array([[
    encode_team(batting_team),   # or your own encoding
    encode_team(bowling_team),
    encode_venue(venue),
    overs,
    runs,
    wickets,
    runs_last5,
    wickets_last5,
    # add more features if your model uses them
]])
```

**b) Encoders** — if you used `LabelEncoder` or `OrdinalEncoder` during training:

```python
import pickle

# Load your saved encoders
with open("team_encoder.pkl", "rb") as f:
    team_enc = pickle.load(f)

with open("venue_encoder.pkl", "rb") as f:
    venue_enc = pickle.load(f)

# Then use them in predict_score():
batting_encoded = team_enc.transform([batting_team])[0]
venue_encoded   = venue_enc.transform([venue])[0]
```

**c) If using a deep learning model (Keras/PyTorch)**:

```python
import tensorflow as tf
model = tf.keras.models.load_model("model.h5")
# or
import torch
model = torch.load("model.pt")
```

### 4. Run the server

```bash
python app.py
```

Open your browser at: **http://localhost:5000**

---

## API Reference

### `POST /api/predict`

**Request body (JSON):**

```json
{
  "batting_team":  "Mumbai Indians",
  "bowling_team":  "Chennai Super Kings",
  "venue":         "Wankhede Stadium, Mumbai",
  "overs":         12.3,
  "runs":          98,
  "wickets":       3,
  "runs_last5":    52,
  "wickets_last5": 1
}
```

**Response:**

```json
{
  "predicted_score": 178,
  "score_range":     "169–186",
  "lower":           169,
  "upper":           186
}
```

### `GET /api/options`

Returns all available teams and venues for the frontend dropdowns.

---

## Input Fields Explained

| Field           | Description                         | Valid Range     |
|-----------------|-------------------------------------|-----------------|
| `batting_team`  | Team currently batting              | Any IPL team    |
| `bowling_team`  | Team currently bowling              | Any IPL team    |
| `venue`         | Stadium where match is being played | Any IPL venue   |
| `overs`         | Current over number                 | 5.0 – 19.5      |
| `runs`          | Runs scored so far                  | 0 – 400         |
| `wickets`       | Wickets lost so far                 | 0 – 9           |
| `runs_last5`    | Runs scored in the last 5 overs     | 0 – 150         |
| `wickets_last5` | Wickets lost in the last 5 overs    | 0 – 5           |

---

## Adding More Teams or Venues

Edit the `TEAMS` and `VENUES` lists in `app.py`:

```python
TEAMS = [
    "Chennai Super Kings",
    "Your New Team",
    # ...
]
```
