from flask import Flask, render_template, request, jsonify
import pandas as pd
import joblib
from datetime import datetime
import logging

app = Flask(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Load model and data
model_data = joblib.load("final_crop_model3.pkl")
model = model_data["model"]
encoders = model_data["encoders"]
feature_cols = model_data["feature_cols"]

df = pd.read_csv("final_complete_data.csv")
logging.info(f"Data loaded successfully! Shape: {df.shape}")

def predict_price(district, market, commodity, variety, grade, date_str):
    try:
        date = pd.to_datetime(date_str, errors='coerce')
        if pd.isna(date):
            return {"success": False, "error": "Invalid date format"}
        
        def encode_value(col, val):
            le = encoders[col]
            if val in le.classes_:
                return le.transform([val])[0]
            else:
                return 0
        
        features = {
            "District_Name_encoded": encode_value("District_Name", district),
            "Market_Name_encoded": encode_value("Market_Name", market),
            "Commodity_encoded": encode_value("Commodity", commodity),
            "Variety_encoded": encode_value("Variety", variety),
            "Grade_encoded": encode_value("Grade", grade),
            "Year": date.year,
            "Month": date.month,
            "Day": date.day,
            "DayOfYear": date.timetuple().tm_yday,
            "WeekOfYear": date.isocalendar()[1],
            "Price_Lag_7": 1500,
            "Price_Lag_30": 1400
        }
        
        input_data = pd.DataFrame([features])
        input_data = input_data.reindex(columns=feature_cols, fill_value=0)
        
        pred = model.predict(input_data)[0]
        
        return {
            "success": True,
            "predicted_price": round(float(pred), 2),
            "district": district,
            "market": market,
            "commodity": commodity,
            "variety": variety,
            "grade": grade,
            "date": date_str
        }
    except Exception as e:
        logging.error(f"Error during prediction: {e}")
        return {"success": False, "error": str(e)}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/options')
def get_options():
    return jsonify({
        "districts": sorted(list(encoders['District_Name'].classes_)),
        "markets": sorted([m for m in df['Market'].dropna().unique() if str(m).strip()]),
        "commodities": sorted(list(encoders['Commodity'].classes_)),
        "varieties": sorted(list(encoders['Variety'].classes_)),
        "grades": sorted(list(encoders['Grade'].classes_))
    })

@app.route('/api/predict', methods=['POST'])
def predict():
    data = request.json
    result = predict_price(
        data.get('district'),
        data.get('market', ''),
        data.get('commodity'),
        data.get('variety', ''),
        data.get('grade', ''),
        data.get('date')
    )
    return jsonify(result)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=False)
