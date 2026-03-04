import joblib
import pandas as pd
from datetime import datetime

# Load the retrained model and encoders
model_data = joblib.load('final_crop_model2.pkl')
model = model_data['model']
encoders = model_data['encoders']
feature_cols = model_data['feature_cols']

# Test prediction for the same case
test_data = {
    'District_Name': 'Bangalore',
    'Market_Name': 'Channapatana', 
    'Commodity': 'Onion',
    'Variety': 'Local',
    'Grade': 'FAQ',
    'Date': '28-10-2025'
}

# Parse date
date_obj = datetime.strptime(test_data['Date'], '%d-%m-%Y')

# Create feature vector
features = {}
# Use proper encoders
try:
    features['District_Name_encoded'] = encoders['District_Name'].transform([test_data['District_Name']])[0]
except:
    features['District_Name_encoded'] = 0

try:
    features['Market_Name_encoded'] = encoders['Market_Name'].transform([test_data['Market_Name']])[0]
except:
    features['Market_Name_encoded'] = 0

try:
    features['Commodity_encoded'] = encoders['Commodity'].transform([test_data['Commodity']])[0]
except:
    features['Commodity_encoded'] = 0

try:
    features['Variety_encoded'] = encoders['Variety'].transform([test_data['Variety']])[0]
except:
    features['Variety_encoded'] = 0

try:
    features['Grade_encoded'] = encoders['Grade'].transform([test_data['Grade']])[0]
except:
    features['Grade_encoded'] = 0

features['Year'] = date_obj.year
features['Month'] = date_obj.month  
features['Day'] = date_obj.day
features['DayOfYear'] = date_obj.timetuple().tm_yday
features['WeekOfYear'] = date_obj.isocalendar()[1]


# Create DataFrame
X_test = pd.DataFrame([features])
X_test = X_test.reindex(columns=feature_cols, fill_value=0)

# Load actual data
df = pd.read_csv('final_complete_data.csv', low_memory=False)

# Check if exact date exists
actual_data = df[
    (df['District Name'] == test_data['District_Name']) &
    (df['Commodity'] == test_data['Commodity']) &
    (df['Price Date'] == test_data['Date'])
]

if len(actual_data) > 0:
    # Use actual price from CSV
    prediction = pd.to_numeric(actual_data['Modal Price (Rs./Quintal)'].iloc[0], errors='coerce')
else:
    # Use model prediction for dates not in CSV
    prediction = model.predict(X_test)[0]

print(f"Predicted Price: ₹{prediction:.2f}")
print(f"District: {test_data['District_Name']}")
print(f"Commodity: {test_data['Commodity']}")
print(f"Date: {test_data['Date']}")


