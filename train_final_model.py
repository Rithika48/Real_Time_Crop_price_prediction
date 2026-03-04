import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score
import joblib

# Load data
df = pd.read_csv('final_complete_data.csv', header=None, names=['District','Market','Commodity','Variety','Grade','Min_Price','Max_Price','Modal_Price','Date'])
df = df[df['Date'] != 'Price Date']  # Remove header rows

# Convert to numeric and datetime
df['Min_Price'] = pd.to_numeric(df['Min_Price'], errors='coerce')
df['Max_Price'] = pd.to_numeric(df['Max_Price'], errors='coerce')
df['Modal_Price'] = pd.to_numeric(df['Modal_Price'], errors='coerce')
df['Date'] = pd.to_datetime(df['Date'], format='%d-%m-%Y', errors='coerce')
df = df.dropna()
df['Year'] = df['Date'].dt.year
df['Month'] = df['Date'].dt.month
df['Day'] = df['Date'].dt.day

# Encode categorical variables
encoders = {}
for col in ['District','Commodity','Variety','Grade']:
    encoders[col] = LabelEncoder()
    df[col + '_encoded'] = encoders[col].fit_transform(df[col])

# Features and target
X = df[['District_encoded','Commodity_encoded','Variety_encoded','Grade_encoded','Year','Month','Day']]
y = df['Modal_Price']

# Train model
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
model = RandomForestRegressor(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# Evaluate
y_pred = model.predict(X_test)
print(f"R² Score: {r2_score(y_test, y_pred):.4f}")
print(f"MAE: {mean_absolute_error(y_test, y_pred):.2f}")

# Save model
joblib.dump(model, 'final_crop_model5.pkl')
joblib.dump(encoders, 'final_encoders5.pkl')
print("Model saved successfully")