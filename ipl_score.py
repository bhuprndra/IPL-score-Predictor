import pandas as pd
import numpy as np
import pickle
import joblib
import warnings


warnings.filterwarnings("ignore")

# LOAD DATASETS
deliveries = pd.read_csv("B:\\bhupendra_codding\\PROJECTS\\ipl-predictor\\dataset\\deliveries.csv")
matches = pd.read_csv("B:\\bhupendra_codding\\PROJECTS\\ipl-predictor\\dataset\\matches.csv")

# TEAM NAME NORMALIZATION
deliveries['batting_team'] = deliveries['batting_team'].replace({
    'Delhi Daredevils': 'Delhi Capitals',
    'Kings XI Punjab': 'Punjab Kings',
    'Deccan Chargers': 'Sunrisers Hyderabad'
})

deliveries['bowling_team'] = deliveries['bowling_team'].replace({
    'Delhi Daredevils': 'Delhi Capitals',
    'Kings XI Punjab': 'Punjab Kings',
    'Deccan Chargers': 'Sunrisers Hyderabad'
})

# VALID IPL TEAMS
teams = [
    'Chennai Super Kings',
    'Delhi Capitals',
    'Punjab Kings',
    'Kolkata Knight Riders',
    'Mumbai Indians',
    'Rajasthan Royals',
    'Royal Challengers Bangalore',
    'Sunrisers Hyderabad',
    'Lucknow Super Giants',
    'Gujarat Titans'
]

deliveries = deliveries[
    deliveries['batting_team'].isin(teams) &
    deliveries['bowling_team'].isin(teams)
]

# MATCH CITY
match_city = matches[['id', 'city']]
deliveries = deliveries.merge(
    match_city,
    left_on='match_id',
    right_on='id'
)

# FIRST INNINGS ONLY
first_innings = deliveries[deliveries['inning'] == 1]

# CURRENT SCORE
first_innings['current_score'] = (
    first_innings.groupby('match_id')['total_runs']
    .cumsum()
)

# BALLS BOWLED
first_innings['balls_bowled'] = (
    first_innings['over'] * 6 +
    first_innings['ball']
)

first_innings['overs'] = (
    first_innings['balls_bowled'] / 6
).round(1)


# WICKETS FALLEN
first_innings['is_wicket'] = (
    first_innings['player_dismissed']
    .notnull()
    .astype(int)
)

first_innings['wickets'] = (
    first_innings.groupby('match_id')['is_wicket']
    .cumsum()
)


# RUNS LAST 5 OVERS
first_innings['runs_last_5'] = (
    first_innings.groupby('match_id')['total_runs']
    .rolling(window=30, min_periods=1)
    .sum()
    .reset_index(level=0, drop=True)
)

# WICKETS LAST 5 OVERS

first_innings['wickets_last_5'] = (
    first_innings.groupby('match_id')['is_wicket']
    .rolling(window=30, min_periods=1)
    .sum()
    .reset_index(level=0, drop=True)
)

# FINAL SCORE
final_score = (
    first_innings.groupby('match_id')['total_runs']
    .sum()
    .reset_index()
)

final_score.columns = ['match_id', 'final_score']

first_innings = first_innings.merge(
    final_score,
    on='match_id'
)

# REQUIRED FEATURES
model_data = first_innings[
    [
        'batting_team',
        'bowling_team',
        'city',
        'current_score',
        'overs',
        'wickets',
        'runs_last_5',
        'wickets_last_5',
        'final_score'
    ]
]

model_data.dropna(inplace=True)

# Ignore very early overs
model_data = model_data[model_data['overs'] >= 5]

print(model_data.head())

# TRAIN MODEL
from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error

X = model_data.drop('final_score', axis=1)
y = model_data['final_score']

x_train, x_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42
)

preprocessor = ColumnTransformer(
    [
        (
            'cat',
            OneHotEncoder(handle_unknown='ignore'),
            ['batting_team', 'bowling_team', 'city']
        )
    ],
    remainder='passthrough'
)

model = Pipeline([
    ('preprocessor', preprocessor),
    ('regressor', RandomForestRegressor(
        n_estimators=100,
        max_depth=20,
        random_state=42,
        n_jobs=-1
    ))
])

print("Training model...")

model.fit(x_train, y_train)

pred = model.predict(x_test)

mae = mean_absolute_error(y_test, pred)

print("MAE =", mae)


joblib.dump(model, 'model.joblib', compress=3)
print("Model saved successfully as model.pkl")