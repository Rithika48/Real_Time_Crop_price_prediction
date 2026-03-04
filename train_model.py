import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import TimeSeriesSplit
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import xgboost as xgb
import joblib
from datetime import datetime
import os

# -----------------------
# CONFIG
# -----------------------
DATA_PATH = "final_complete_data.csv"
MODEL_PATH = "final_crop_model7.pkl"

# -----------------------
# LOAD DATA
# -----------------------
df = pd.read_csv(DATA_PATH, low_memory=False)
print("Original Columns:", df.columns.tolist())

# -----------------------
# CLEAN / RENAME COLUMNS
# -----------------------
df.columns = df.columns.str.strip()

rename_map = {
    'Modal Price (Rs./Quintal)': 'Modal_Price',
    'Min Price (Rs./Quintal)': 'Min_Price', 
    'Max Price (Rs./Quintal)': 'Max_Price',
    'Price Date': 'Date',
    'District Name': 'District_Name',
    'Market Name': 'Market_Name'
}
df.rename(columns=rename_map, inplace=True)
print("Cleaned Columns:", df.columns.tolist())

# -----------------------
# ENSURE REQUIRED COLUMNS
# -----------------------
required = ['District_Name', 'Market_Name', 'Commodity', 'Variety', 'Grade', 'Modal_Price', 'Date']
for c in required:
    if c not in df.columns:
        raise ValueError(f"Required column missing: {c}")

# -----------------------
# PARSE DATES & CLEAN DATA
# -----------------------
# Handle multiple date formats
def parse_date(date_str):
    try:
        # Try DD-MM-YYYY format first
        return pd.to_datetime(date_str, format='%d-%m-%Y')
    except:
        try:
            # Try DD-MM-YYYY format
            return pd.to_datetime(date_str, format='%d-%m-%Y')
        except:
            # Fallback to automatic parsing
            return pd.to_datetime(date_str, errors='coerce')

df['Date'] = df['Date'].apply(parse_date)

# Clean Modal Price - handle various formats
df['Modal_Price'] = (
    df['Modal_Price'].astype(str)
    .str.replace(',', '', regex=False)
    .str.replace('₹', '', regex=False)
    .str.extract(r'(\d+\.?\d*)')[0]
)
df['Modal_Price'] = pd.to_numeric(df['Modal_Price'], errors='coerce')

# Remove invalid data
df = df.dropna(subset=['Date', 'Modal_Price'])
df = df[df['Modal_Price'] > 0]  # Remove zero/negative prices
df = df.sort_values('Date')

print(f"Rows after cleaning: {len(df)}")
print(f"Date range: {df['Date'].min()} to {df['Date'].max()}")
print(f"Price range: ₹{df['Modal_Price'].min():.2f} to ₹{df['Modal_Price'].max():.2f}")

if len(df) == 0:
    raise ValueError("No data available after cleaning. Check your CSV.")

# -----------------------
# FEATURE ENGINEERING
# -----------------------
df['Year'] = df['Date'].dt.year
df['Month'] = df['Date'].dt.month
df['Day'] = df['Date'].dt.day
df['DayOfYear'] = df['Date'].dt.dayofyear
df['WeekOfYear'] = df['Date'].dt.isocalendar().week

# Add price trend features
df = df.sort_values(['District_Name', 'Market_Name', 'Commodity', 'Date'])
df['Price_Lag_7'] = df.groupby(['District_Name', 'Market_Name', 'Commodity'])['Modal_Price'].shift(7)
df['Price_Lag_30'] = df.groupby(['District_Name', 'Market_Name', 'Commodity'])['Modal_Price'].shift(30)

cat_cols = ['District_Name', 'Market_Name', 'Commodity', 'Variety', 'Grade']
encoders = {}

for col in cat_cols:
    le = LabelEncoder()
    df[col + '_encoded'] = le.fit_transform(df[col].astype(str))
    encoders[col] = le

# -----------------------
# FEATURES & TARGET
# -----------------------
feature_cols = ['District_Name_encoded', 'Market_Name_encoded', 'Commodity_encoded', 
                'Variety_encoded', 'Grade_encoded', 'Year', 'Month', 'Day', 
                'DayOfYear', 'WeekOfYear']

# Add lag features if available
if 'Price_Lag_7' in df.columns:
    feature_cols.extend(['Price_Lag_7', 'Price_Lag_30'])

X = df[feature_cols].fillna(df['Modal_Price'].median())
y = df['Modal_Price']

# -----------------------
# TIME SERIES SPLIT TRAINING
# -----------------------
# Use more recent data for training (last 2 years)
recent_data = df[df['Date'] >= '2023-01-01']
if len(recent_data) > 1000:
    df_train = recent_data
    print(f"Using recent data: {len(df_train)} records from {df_train['Date'].min()}")
else:
    df_train = df
    print(f"Using all data: {len(df_train)} records")

X_train = df_train[feature_cols].fillna(df_train['Modal_Price'].median())
y_train = df_train['Modal_Price']

n_splits = min(5, len(df_train) // 100)
tscv = TimeSeriesSplit(n_splits=n_splits)
best_model = None
best_mae = float('inf')

mae_scores = []
rmse_scores = []

for fold, (train_idx, val_idx) in enumerate(tscv.split(X_train)):
    X_fold_train, X_val = X_train.iloc[train_idx], X_train.iloc[val_idx]
    y_fold_train, y_val = y_train.iloc[train_idx], y_train.iloc[val_idx]

    model = xgb.XGBRegressor(
        n_estimators=300,
        learning_rate=0.1,
        max_depth=5,
        subsample=0.8,
        colsample_bytree=0.8,
        random_state=42,
        objective='reg:squarederror',
        reg_alpha=0.1,
        reg_lambda=0.1
    )

    model.fit(X_fold_train, y_fold_train)
    preds = model.predict(X_val)

    mae = mean_absolute_error(y_val, preds)
    rmse = np.sqrt(mean_squared_error(y_val, preds))
    mae_scores.append(mae)
    rmse_scores.append(rmse)

    print(f"Fold {fold+1} - MAE: {mae:.2f}, RMSE: {rmse:.2f}")

    if mae < best_mae:
        best_mae = mae
        best_model = model

# -----------------------
# FINAL EVALUATION METRICS
# -----------------------
mean_mae = np.mean(mae_scores)
mean_rmse = np.mean(rmse_scores)
r2 = best_model.score(X_val, y_val)
accuracy = r2 * 100

print("\nFINAL MODEL ACCURACY:")
print(f"Average MAE  : {mean_mae:.2f}")
print(f"Average RMSE : {mean_rmse:.2f}")
print(f"R² Score     : {r2:.3f}")
print(f"Final Model Accuracy: {accuracy:.2f}%")

# -----------------------
# SAVE MODEL + ENCODERS + METADATA
# -----------------------
model_data = {
    "model": best_model, 
    "encoders": encoders,
    "feature_cols": feature_cols,
    "training_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    "data_range": f"{df['Date'].min()} to {df['Date'].max()}",
    "total_records": len(df)
}

joblib.dump(model_data, MODEL_PATH)
print(f"\nModel saved to {MODEL_PATH}")
print(f"Training completed with MAE={best_mae:.2f}")
print(f"Model covers data from {df['Date'].min()} to {df['Date'].max()}")

if __name__ == "__main__":
    print("Model training completed successfully!")