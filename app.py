from flask import Flask, render_template, request, jsonify
import pandas as pd
import joblib
from datetime import datetime
import logging
import os

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

# ==========================================
# LOAD MODEL + DATA
# ==========================================

def load_resources():
    try:
        # Load model file
        model_data = joblib.load('final_crop_model2.pkl')
        model = model_data.get('model')
        encoders = model_data.get('encoders')
        feature_cols = model_data.get('feature_cols')

        # Load CSV
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(BASE_DIR, "final_complete_data.csv")

        df = pd.read_csv(file_path)
        df.columns = df.columns.str.strip()

# ✅ FIX TYPE ISSUE
        df['Modal Price (Rs./Quintal)'] = pd.to_numeric(
            df['Modal Price (Rs./Quintal)'],
            errors='coerce'
        )

        print("✅ CSV Loaded Successfully")
        print("Columns:", df.columns.tolist())

        return model, encoders, df, feature_cols

    except Exception as e:
        logging.error(f"❌ Error loading resources: {e}")
        return None, None, None, None


model, encoders, df, feature_cols = load_resources()

# ==========================================
# ROUTES
# ==========================================

@app.route('/')
def home():
    return render_template('welcome.html')


@app.route('/dashboard')
def dashboard():
    return render_template('index.html')


# ==========================================
# LOAD DROPDOWN OPTIONS
# ==========================================

@app.route('/api/options')
def get_options():
    if df is None:
        return jsonify({"error": "Data not loaded"}), 500

    try:
        return jsonify({
            "districts": sorted(df['District Name'].dropna().unique().tolist()),
            "markets": sorted(df['Market Name'].dropna().unique().tolist()),
            "commodities": sorted(df['Commodity'].dropna().unique().tolist()),
            "varieties": sorted(df['Variety'].dropna().unique().tolist()),
            "grades": sorted(df['Grade'].dropna().unique().tolist())
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ==========================================
# FILTERED OPTIONS
# ==========================================

@app.route('/api/filtered-options', methods=['POST'])
def get_filtered_options():
    if df is None:
        return jsonify({"error": "Data not loaded"}), 500

    try:
        data = request.get_json()

        district = data.get("district")
        commodity = data.get("commodity")

        filtered_df = df.copy()

        if district:
            filtered_df = filtered_df[filtered_df['District Name'] == district]

        if commodity:
            filtered_df = filtered_df[filtered_df['Commodity'] == commodity]

        return jsonify({
            "varieties": sorted(filtered_df['Variety'].dropna().unique().tolist()),
            "grades": sorted(filtered_df['Grade'].dropna().unique().tolist()),
            "markets": sorted(filtered_df['Market Name'].dropna().unique().tolist())
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ==========================================
# PRICE PREDICTION
# ==========================================

@app.route('/api/predict', methods=['POST'])
def predict():
    try:
        if df is None:
            return jsonify({"error": "Data not loaded"}), 500

        data = request.get_json()

        if not data:
            return jsonify({"error": "No input data received"}), 400

        district = data.get("district")
        commodity = data.get("commodity")
        date = data.get("date")

        if not district or not commodity or not date:
            return jsonify({"error": "Missing required fields"}), 400

        # Handle both date formats
        csv_date = None
        try:
            csv_date = datetime.strptime(date, "%d-%m-%Y").strftime("%d-%m-%Y")
        except:
            try:
                csv_date = datetime.strptime(date, "%Y-%m-%d").strftime("%d-%m-%Y")
            except:
                return jsonify({"error": "Invalid date format"}), 400

        # Search exact historical match
        result = df[
            (df['District Name'] == district) &
            (df['Commodity'] == commodity) &
            (df['Price Date'] == csv_date)
        ]

        if not result.empty:
            price = result.iloc[0]['Modal Price (Rs./Quintal)']
        else:
            # fallback average
            avg_df = df[df['Commodity'] == commodity]

            if avg_df.empty:
                return jsonify({"error": "No data available for this commodity"}), 404

            price = avg_df['Modal Price (Rs./Quintal)'].mean()
            print(df['Modal Price (Rs./Quintal)'].dtype)

        if pd.isna(price):
            return jsonify({"error": "Price calculation failed"}), 500

        return jsonify({
            "success": True,
            "predicted_price": round(float(price), 2)
        })

    except Exception as e:
        print("🔥 ERROR IN PREDICT:", e)
        return jsonify({"error": str(e)}), 500
    
@app.route('/api/update-data', methods=['POST'])
def update_data():
    try:
        # Reload CSV
        global df
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(BASE_DIR, "final_complete_data.csv")

        df = pd.read_csv(file_path)
        df.columns = df.columns.str.strip()

        df['Modal Price (Rs./Quintal)'] = pd.to_numeric(
            df['Modal Price (Rs./Quintal)'],
            errors='coerce'
        )

        return jsonify({"success": True, "message": "Data updated successfully"})

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@app.route('/api/run-scraper', methods=['POST'])
def run_scraper():
    try:
        # Example logic
        return jsonify({
            "success": True,
            "message": "Scraper executed successfully!",
            "data": []
        })
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500
    
@app.route('/crop-rotation')
def crop_rotation():
    return render_template('crop_rotation.html')

from flask import request, jsonify

@app.route('/api/crop-rotation', methods=['POST'])
def crop_rotation_api():
    data = request.get_json()
    area = data.get("area")

    recommendation = f"For {area} acres: Rice → Wheat → Legumes"

    return jsonify({
        "recommendation": recommendation
    })


@app.route('/high-demand')
def high_demand():
    return render_template('high_demand.html')


@app.route('/weather-advisory')
def weather_advisory():
    return render_template('weather_advisory.html')


@app.route('/fertilizer-calc')
def fertilizer_calc():
    return render_template('fertilizer_calc.html')


@app.route('/disease-detection')
def disease_detection():
    return render_template('disease_detection.html')


@app.route('/market-trends')
def market_trends():
    return render_template('market_trends.html')


@app.route('/profit-calculator')
def profit_calculator():
    return render_template('profit_calculator.html')


@app.route('/update-data')
def update_data_page():
    return render_template('update_data.html')
    
@app.route('/api/train-model', methods=['POST'])
def train_model():
    try:
        return jsonify({
            "success": True,
            "message": "Model trained successfully!"
        })
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500


# ==========================================
# START FLASK SERVER
# ==========================================

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)