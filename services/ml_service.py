# app/services/ml_service.py
import joblib
import numpy as np

# 1. Load your specific model file
try:
    model = joblib.load("pipe.joblib") # <-- Using your file name
    print("ML Model (pipe.joblib) loaded successfully.")
except FileNotFoundError:
    print("Error: pipe.joblib not found. Predictions will not work.")
    model = None
except Exception as e:
    print(f"Error loading model: {e}")
    model = None

# 2. Define a function to get predictions
def get_match_prediction(features: list) -> dict:
    """
    Takes a list of features, formats them for the pipeline,
    and returns a prediction dictionary.
    """
    if model is None:
        return {"error": "Model not loaded"}

    try:
        # Your ColumnTransformer expects a 2D array:
        # 1st 3 are categorical, next 6 are numerical
        # We wrap our single sample in another list
        features_array = [features]
        
        # .predict_proba() returns probabilities for [class_0, class_1]
        # In your case, this is likely [Losing Probability, Winning Probability]
        probabilities = model.predict_proba(features_array)
        
        # Get the probability for "Win" (the second class, index 1)
        winning_prob = probabilities[0][1] 
        losing_prob = probabilities[0][0] # or (1 - winning_prob)
        
        # Your model predicts the probability of the *batting team* winning
        return {
            "team_a_win_prob": winning_prob, # Batting team
            "team_b_win_prob": losing_prob   # Bowling team
        }
        
    except Exception as e:
        return {
            "error": f"Prediction failed: {e}"
        }