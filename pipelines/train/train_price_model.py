import os
import pickle
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.metrics import mean_absolute_error
from xgboost import XGBRegressor
from sklearn.ensemble import GradientBoostingRegressor


def train_price_models():
    print("Loading data for advanced price models...")
    features_path = os.path.join(os.path.dirname(__file__), "..", "..", "data", "features.parquet")
    if os.path.exists(features_path):
        df = pd.read_parquet(features_path)
    else:
        print("Features not built, run build_features.py first!")
        return

    # Train on won only for price models
    train_df = df[df["won"] == 1.0].copy()

    features = [
        "make",
        "fuel_type",
        "body_type",
        "channel",
        "vehicle_age",
        "mileage",
        "damage_severity_score",
        "risk_score",
    ]
    target = "sale_price"

    X = train_df[features]
    y = train_df[target]

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    categorical_features = ["make", "fuel_type", "body_type", "channel"]
    numeric_features = ["vehicle_age", "mileage", "damage_severity_score", "risk_score"]

    preprocessor = ColumnTransformer(
        transformers=[
            ("num", StandardScaler(), numeric_features),
            (
                "cat",
                OneHotEncoder(handle_unknown="ignore", sparse_output=False),
                categorical_features,
            ),
        ]
    )

    print("Training Upgraded XGBRegressor...")
    price_model = Pipeline(
        steps=[
            ("preprocessor", preprocessor),
            (
                "model",
                XGBRegressor(n_estimators=150, learning_rate=0.05, max_depth=5, random_state=42),
            ),
        ]
    )
    price_model.fit(X_train, y_train)

    y_pred = price_model.predict(X_test)
    print(f"Point Estimate MAE: {mean_absolute_error(y_test, y_pred):.2f}")

    print("Training QuantileRegressor (q=0.10)...")
    q10_model = Pipeline(
        steps=[
            ("preprocessor", preprocessor),
            (
                "model",
                GradientBoostingRegressor(
                    loss="quantile", alpha=0.10, n_estimators=100, random_state=42
                ),
            ),
        ]
    )
    q10_model.fit(X_train, y_train)

    print("Training QuantileRegressor (q=0.90)...")
    q90_model = Pipeline(
        steps=[
            ("preprocessor", preprocessor),
            (
                "model",
                GradientBoostingRegressor(
                    loss="quantile", alpha=0.90, n_estimators=100, random_state=42
                ),
            ),
        ]
    )
    q90_model.fit(X_train, y_train)

    model_dir = os.path.join(os.path.dirname(__file__), "..", "..", "models")
    os.makedirs(model_dir, exist_ok=True)

    with open(os.path.join(model_dir, "price_model.pkl"), "wb") as f:
        pickle.dump(price_model, f)
    with open(os.path.join(model_dir, "price_q10.pkl"), "wb") as f:
        pickle.dump(q10_model, f)
    with open(os.path.join(model_dir, "price_q90.pkl"), "wb") as f:
        pickle.dump(q90_model, f)

    print(f"Saved upgraded price models to {os.path.abspath(model_dir)}")


if __name__ == "__main__":
    train_price_models()
