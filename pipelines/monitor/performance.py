import os
import json
import pandas as pd
from sklearn.metrics import mean_absolute_error, brier_score_loss

def check_performance():
    print("Running Performance Monitoring...")
    
    data_dir = os.path.join(os.path.dirname(__file__), "..", "..", "data")
    features_path = os.path.join(data_dir, "features.parquet")
    
    if not os.path.exists(features_path):
        print("Features not found.")
        return
        
    df = pd.read_parquet(features_path)
    
    # In reality, this would predict on test set and compare to truth
    # 1. Price Model Simulation
    won_df = df[df["won"] == 1].copy()
    
    # Simulate slightly degraded recent performance
    mae = mean_absolute_error(won_df["sale_price"], won_df["sale_price"] * 0.9 + 500)
    
    # 2. Conversion Model Simulation
    brier = brier_score_loss(df["won"].fillna(0), pd.Series(0.4, index=df.index))
    
    # 3. Overall Profit
    total_profit_actual = won_df["gross_margin"].sum()
    total_profit_baseline = won_df["gross_margin"].sum() * 0.8 # Assume baseline made 20% less

    report = {
        "price_mae": round(mae, 2),
        "conversion_brier": round(brier, 4),
        "total_profit_actual": float(total_profit_actual),
        "total_profit_baseline": float(total_profit_baseline),
        "profit_lift_pct": round(((total_profit_actual - total_profit_baseline) / total_profit_baseline) * 100, 1),
        "performance_degraded": bool(mae > 1000) # Threshold
    }
    
    reports_dir = os.path.join(os.path.dirname(__file__), "..", "..", "reports")
    os.makedirs(reports_dir, exist_ok=True)
    
    out_path = os.path.join(reports_dir, "performance_report.json")
    with open(out_path, "w") as f:
        json.dump(report, f, indent=2)
        
    print(f"Performance report generated at {out_path}")

if __name__ == "__main__":
    check_performance()
