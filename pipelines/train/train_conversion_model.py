import os
import pickle
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.calibration import CalibratedClassifierCV
from sklearn.metrics import roc_auc_score, brier_score_loss

def train_conversion_model():
    print("Loading data for advanced conversion model...")
    # Read from features if available, else fallback
    features_path = os.path.join(os.path.dirname(__file__), "..", "..", "data", "features.parquet")
    if os.path.exists(features_path):
        df = pd.read_parquet(features_path)
    else:
        print("Features not built, run build_features.py first!")
        return

    df["won"] = df["won"].fillna(0).astype(int)
    
    features = [
        "make", "fuel_type", "body_type", "channel", 
        "vehicle_age", "mileage", "offer_price", 
        "damage_severity_score", "risk_score", "month_sin", "month_cos"
    ]
    target = "won"

    X = df[features]
    y = df[target]

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    categorical_features = ["make", "fuel_type", "body_type", "channel"]
    numeric_features = ["vehicle_age", "mileage", "offer_price", "damage_severity_score", "risk_score", "month_sin", "month_cos"]

    preprocessor = ColumnTransformer(
        transformers=[
            ("num", "passthrough", numeric_features), # HistGradientBoosting handles unscaled 
            ("cat", OneHotEncoder(handle_unknown="ignore", sparse_output=False), categorical_features),
        ]
    )

    print("Training HistGradientBoostingClassifier with Calibration...")
    base_model = Pipeline(steps=[
        ("preprocessor", preprocessor),
        ("model", HistGradientBoostingClassifier(
            max_iter=200, learning_rate=0.05, random_state=42, 
            early_stopping=True, validation_fraction=0.1
        ))
    ])
    
    calibrated_model = CalibratedClassifierCV(estimator=base_model, method="isotonic", cv=3)
    calibrated_model.fit(X_train, y_train)

    y_pred_prob = calibrated_model.predict_proba(X_test)[:, 1]
    
    print(f"Conversion Model ROC AUC: {roc_auc_score(y_test, y_pred_prob):.3f}")
    print(f"Conversion Model Brier Score: {brier_score_loss(y_test, y_pred_prob):.3f}")

    model_dir = os.path.join(os.path.dirname(__file__), "..", "..", "models")
    os.makedirs(model_dir, exist_ok=True)
    
    with open(os.path.join(model_dir, "conversion_model.pkl"), "wb") as f:
        pickle.dump(calibrated_model, f)
        
    print(f"Saved upgraded conversion model to {os.path.abspath(model_dir)}")

if __name__ == "__main__":
    train_conversion_model()
