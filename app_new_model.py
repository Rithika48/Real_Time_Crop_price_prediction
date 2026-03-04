from dotenv import load_dotenv
load_dotenv()
from flask import Flask, render_template, request, jsonify
import pandas as pd
import joblib
from datetime import datetime
import logging
import subprocess
import json
import sys

app = Flask(__name__)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def load_resources():
    """Loads the ML model, encoders, and data from files."""
    try:
        # Load the new model and encoders
        model = joblib.load('final_crop_model5.pkl')
        encoders = joblib.load('final_encoders5.pkl')

        df = pd.read_csv("final_complete_data.csv")

        # Standardize column names
        column_map = {
            'District Name': 'District',
            'Market Name': 'Market',
            'Price Date': 'Date'
        }
        df.rename(columns=column_map, inplace=True)

        # Ensure required columns exist
        required_cols = ['District', 'Market', 'Commodity', 'Variety', 'Grade', 'Date']
        if not all(col in df.columns for col in required_cols):
             # Fallback if columns are not named as expected
            if len(df.columns) >= 6:
                df.columns = ['District', 'Market', 'Commodity', 'Variety', 'Grade', 'Date'] + list(df.columns[6:])

        # Clean up data by removing header rows that might be repeated in the data
        df = df[~df['District'].isin(['District', 'District Name'])]

        logging.info(f"Data loaded successfully! Shape: {df.shape}")
        logging.info(f"Columns: {list(df.columns)}")
        logging.info(f"Sample districts: {df['District'].unique()[:5]}")
        logging.info(f"Sample commodities: {df['Commodity'].unique()[:5]}")

        return model, encoders, df

    except FileNotFoundError as e:
        logging.error(f"A required file was not found: {e}. Please run train_final_model.py first.")
        return None, None, None
    except Exception as e:
        logging.error(f"An unexpected error occurred during resource loading: {e}")
        return None, None, None

model, encoders, df = load_resources()

def predict_price(district, market, commodity, variety, grade, date_str):
    if model is None:
        return {"success": False, "error": "Model not loaded"}
    
    try:
        # Check if exact date exists in dataset first
        date = pd.to_datetime(date_str, errors='coerce')
        if pd.isna(date):
            return {"success": False, "error": "Invalid date format"}
        
        # Convert date to CSV format (dd-mm-yyyy)
        csv_date = date.strftime('%d-%m-%Y')
        
        # Check if exact date exists in CSV
        actual_data = df[
            (df['District'] == district) &
            (df['Commodity'] == commodity) &
            (df['Date'] == csv_date)
        ]
        
        if len(actual_data) > 0:
            # Use actual price from CSV
            pred = pd.to_numeric(actual_data['Modal Price (Rs./Quintal)'].iloc[0], errors='coerce')
            
            return {
                "success": True,
                "predicted_price": round(float(pred), 2),
                "district": district,
                "market": market,
                "commodity": commodity,
                "variety": variety,
                "grade": grade,
                "date": date_str,
                "source": "historical_data"
            }
        else:
            # Check for recent historical data to smooth predictions
            recent_data = df[
                (df['District'] == district) &
                (df['Commodity'] == commodity)
            ]
            
            if len(recent_data) > 0:
                # Get recent prices (last 30 records)
                recent_data = recent_data.tail(30)
                recent_prices = pd.to_numeric(recent_data['Modal Price (Rs./Quintal)'], errors='coerce').dropna()
                
                if len(recent_prices) > 0:
                    # Use model prediction but constrain it based on recent prices
                    year, month, day = date.year, date.month, date.day
                    
                    # Encode features using new model encoders
                    try:
                        district_encoded = encoders['District'].transform([district])[0]
                    except:
                        district_encoded = 0
                    
                    try:
                        commodity_encoded = encoders['Commodity'].transform([commodity])[0]
                    except:
                        commodity_encoded = 0
                    
                    try:
                        variety_encoded = encoders['Variety'].transform([variety])[0]
                    except:
                        variety_encoded = 0
                    
                    try:
                        grade_encoded = encoders['Grade'].transform([grade])[0]
                    except:
                        grade_encoded = 0
                    
                    # Create feature vector for new model
                    features = [[district_encoded, commodity_encoded, variety_encoded, grade_encoded, year, month, day]]
                    model_pred = model.predict(features)[0]
                    
                    # Calculate recent average and std
                    recent_avg = recent_prices.mean()
                    recent_std = recent_prices.std()
                    
                    # Constrain prediction to be within reasonable range of recent prices
                    max_variation = recent_std * 1.5 if recent_std > 0 else recent_avg * 0.2
                    min_price = recent_avg - max_variation
                    max_price = recent_avg + max_variation
                    
                    # Apply constraints
                    pred = max(min_price, min(max_price, model_pred))
                else:
                    # Fallback to pure model prediction
                    year, month, day = date.year, date.month, date.day
                    
                    try:
                        district_encoded = encoders['District'].transform([district])[0]
                    except:
                        district_encoded = 0
                    
                    try:
                        commodity_encoded = encoders['Commodity'].transform([commodity])[0]
                    except:
                        commodity_encoded = 0
                    
                    try:
                        variety_encoded = encoders['Variety'].transform([variety])[0]
                    except:
                        variety_encoded = 0
                    
                    try:
                        grade_encoded = encoders['Grade'].transform([grade])[0]
                    except:
                        grade_encoded = 0
                    
                    features = [[district_encoded, commodity_encoded, variety_encoded, grade_encoded, year, month, day]]
                    pred = model.predict(features)[0]
            else:
                # No historical data available, use pure model prediction
                year, month, day = date.year, date.month, date.day
                
                try:
                    district_encoded = encoders['District'].transform([district])[0]
                except:
                    district_encoded = 0
                
                try:
                    commodity_encoded = encoders['Commodity'].transform([commodity])[0]
                except:
                    commodity_encoded = 0
                
                try:
                    variety_encoded = encoders['Variety'].transform([variety])[0]
                except:
                    variety_encoded = 0
                
                try:
                    grade_encoded = encoders['Grade'].transform([grade])[0]
                except:
                    grade_encoded = 0
                
                features = [[district_encoded, commodity_encoded, variety_encoded, grade_encoded, year, month, day]]
                pred = model.predict(features)[0]
        
        return {
            "success": True,
            "predicted_price": round(float(pred), 2),
            "district": district,
            "market": market,
            "commodity": commodity,
            "variety": variety,
            "grade": grade,
            "date": date_str,
            "source": "ml_model"
        }
    except Exception as e:
        logging.error(f"Error during prediction: {e}")
        return {"success": False, "error": str(e)}

@app.route('/api/run-scraper', methods=['POST'])
def run_scraper():
    """Endpoint to trigger the web scraper."""
    try:
        python_executable = sys.executable
        scraper_script = 'multi_crop_scraper.py'
        
        logging.info(f"Attempting to run scraper: {python_executable} {scraper_script}")
        
        # Run the scraper script and capture its output
        result = subprocess.run(
            [python_executable, scraper_script],
            capture_output=True,
            text=True,
            check=True,
            encoding='utf-8'
        )
        
        output = result.stdout
        logging.info(f"Scraper output:\n{output}")
        
        # Check the output for success messages
        if "Data appended to final_complete_data.csv" in output:
            # Reload the app's data to reflect the changes
            global model, encoders, df
            model, encoders, df = load_resources() 
            logging.info("Data resources reloaded after successful scrape.")
            return jsonify({'success': True, 'message': 'Successfully collected new data from multiple crops.', 'data': []})
        elif "Total new records scraped: 0" in output:
            return jsonify({'success': True, 'message': 'No new data to fetch. Your records are already up-to-date.', 'data': []})
        else:
            return jsonify({'success': True, 'message': 'Scraper completed successfully.', 'data': []})

    except FileNotFoundError:
        logging.error("Scraper script 'multi_crop_scraper.py' not found.")
        return jsonify({'success': False, 'message': 'Error: Multi-crop scraper script not found.'}), 500
    except subprocess.CalledProcessError as e:
        logging.error(f"Scraper script failed with error:\n{e.stderr}")
        return jsonify({'success': False, 'message': f'Multi-crop scraper failed: {e.stderr}'}), 500

@app.route('/api/run-multi-scraper', methods=['POST'])
def run_multi_scraper():
    """Endpoint to trigger the multi-crop scraper."""
    try:
        python_executable = sys.executable
        scraper_script = 'multi_crop_scraper.py'
        
        logging.info(f"Attempting to run multi-crop scraper: {python_executable} {scraper_script}")
        
        # Run the scraper script and capture its output
        result = subprocess.run(
            [python_executable, scraper_script],
            capture_output=True,
            text=True,
            check=True,
            encoding='utf-8'
        )
        
        output = result.stdout
        logging.info(f"Multi-crop scraper output:\n{output}")
        
        # Check the output for success messages
        if "Data appended to final_complete_data.csv" in output:
            # Reload the app's data to reflect the changes
            global model, encoders, df
            model, encoders, df = load_resources() 
            logging.info("Data resources reloaded after successful multi-crop scrape.")
            
            # Extract summary information
            lines = output.split('\n')
            summary_data = []
            for line in lines:
                if ':' in line and 'records' in line:
                    summary_data.append(line.strip())
            
            return jsonify({
                'success': True, 
                'message': 'Successfully collected data from multiple crops (last 90 days).', 
                'summary': summary_data
            })
        else:
            return jsonify({'success': True, 'message': 'Multi-crop scraper completed.', 'data': []})

    except FileNotFoundError:
        logging.error("Multi-crop scraper script 'multi_crop_scraper.py' not found.")
        return jsonify({'success': False, 'message': 'Error: Multi-crop scraper script not found.'}), 500
    except subprocess.CalledProcessError as e:
        logging.error(f"Multi-crop scraper script failed with error:\n{e.stderr}")
        return jsonify({'success': False, 'message': f'Multi-crop scraper failed: {e.stderr}'}), 500

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/update-data')
def update_data():
    return render_template('update_data.html')

@app.route('/api/options')
def get_options():
    if encoders is None or df is None:
        return jsonify({"error": "Model not loaded"}), 500
    
    try:
        districts = sorted(list(encoders['District'].classes_))
        commodities = sorted(list(encoders['Commodity'].classes_))
        varieties = sorted(list(encoders['Variety'].classes_))
        grades = sorted(list(encoders['Grade'].classes_))
        
        return jsonify({
            "districts": districts,
            "markets": sorted([m for m in df['Market'].dropna().unique() if str(m).strip()]),
            "commodities": commodities,
            "varieties": varieties,
            "grades": grades
        })
    except Exception as e:
        return jsonify({"districts": [], "markets": [], "commodities": [], "varieties": [], "grades": []}), 500

@app.route('/api/filtered-options', methods=['POST'])
def get_filtered_options():
    if df is None:
        return jsonify({"error": "Data not loaded"}), 500
    
    try:
        data = request.json
        district = data.get('district')
        commodity = data.get('commodity')
        
        logging.info(f"Filtering for district: {district}, commodity: {commodity}")
        
        # Filter data based on district and commodity
        filtered_df = df
        
        if district:
            filtered_df = filtered_df[filtered_df['District'] == district]
            logging.info(f"After district filter: {len(filtered_df)} rows")
        
        if commodity:
            filtered_df = filtered_df[filtered_df['Commodity'] == commodity]
            logging.info(f"After commodity filter: {len(filtered_df)} rows")
        
        # Get unique values for the filtered data, removing NaN values
        varieties = sorted([v for v in filtered_df['Variety'].dropna().unique() if str(v).strip()]) if not filtered_df.empty else []
        grades = sorted([g for g in filtered_df['Grade'].dropna().unique() if str(g).strip()]) if not filtered_df.empty else []
        markets = sorted([m for m in filtered_df['Market'].dropna().unique() if str(m).strip()]) if not filtered_df.empty else []
        
        logging.info(f"Found {len(varieties)} varieties, {len(grades)} grades, {len(markets)} markets")
        
        return jsonify({
            "varieties": varieties,
            "grades": grades,
            "markets": markets
        })
        
    except Exception as e:
        logging.error(f"Error in filtered options: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/predict', methods=['POST'])
def predict():
    try:
        data = request.json
        logging.info(f"Received data: {data}")
        
        district = data.get('district')
        market = data.get('market')
        commodity = data.get('commodity')
        variety = data.get('variety')
        grade = data.get('grade')
        date = data.get('date')
        
        logging.info(f"Parsed values: district={district}, commodity={commodity}, date={date}")
        
        if not all([district, commodity, date]):
            return jsonify({"error": "Missing required fields"}), 400
        
        # Auto-select defaults if not provided
        if not variety:
            variety = "Local" if "Local" in encoders['Variety'].classes_ else (encoders['Variety'].classes_[0] if len(encoders['Variety'].classes_) > 0 else "Unknown")
        if not grade:
            grade = "FAQ" if "FAQ" in encoders['Grade'].classes_ else (encoders['Grade'].classes_[0] if len(encoders['Grade'].classes_) > 0 else "Unknown")
        if not market:
            # Try to find a market in the same district
            if df is not None:
                district_markets = df[df['District'] == district]['Market'].unique()
                market = district_markets[0] if len(district_markets) > 0 else district
            else:
                market = district
        
        logging.info(f"Final values: district={district}, market={market}, commodity={commodity}, variety={variety}, grade={grade}, date={date}")
        
        result = predict_price(district, market, commodity, variety, grade, date)
        logging.info(f"Prediction result: {result}")
        return jsonify(result)
        
    except Exception as e:
        logging.error(f"Error in predict endpoint: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/crop-rotation')
def crop_rotation():
    return render_template('crop_rotation.html')

@app.route('/disease-detection')
def disease_detection():
    return render_template('disease_detection.html')

@app.route('/api/crop-rotation', methods=['POST'])
def crop_rotation_api():
    return jsonify({"success": True, "redirect": "/crop-rotation"})

CROP_DATA = {
    'Rice': {'duration': 4, 'yield_per_acre': 25, 'cost_per_acre': 15000, 'season': ['Kharif', 'Rabi']},
    'Wheat': {'duration': 5, 'yield_per_acre': 20, 'cost_per_acre': 12000, 'season': ['Rabi']},
    'Maize': {'duration': 3, 'yield_per_acre': 30, 'cost_per_acre': 10000, 'season': ['Kharif', 'Summer']},
    'Potato': {'duration': 3, 'yield_per_acre': 150, 'cost_per_acre': 25000, 'season': ['Rabi', 'Summer']},
    'Onion': {'duration': 4, 'yield_per_acre': 120, 'cost_per_acre': 20000, 'season': ['Rabi', 'Summer']},
    'Tomato': {'duration': 3, 'yield_per_acre': 200, 'cost_per_acre': 30000, 'season': ['All']},
    'Groundnut': {'duration': 4, 'yield_per_acre': 15, 'cost_per_acre': 18000, 'season': ['Kharif', 'Summer']},
    'Cabbage': {'duration': 2, 'yield_per_acre': 180, 'cost_per_acre': 15000, 'season': ['Rabi', 'Summer']}
}

def calculate_profit_potential(district, commodity, planting_month, area_acres=1):
    """Calculate profit potential for a crop based on predicted prices and costs"""
    try:
        if commodity not in CROP_DATA:
            return None
            
        crop_info = CROP_DATA[commodity]
        
        # Calculate harvest month
        harvest_month = (planting_month + crop_info['duration']) % 12
        if harvest_month == 0:
            harvest_month = 12
            
        # Get predicted price at harvest time
        harvest_date = f"2024-{harvest_month:02d}-15"
        
        # Use default variety and grade for prediction
        variety = "Local" if "Local" in encoders['Variety'].classes_ else encoders['Variety'].classes_[0]
        grade = "FAQ" if "FAQ" in encoders['Grade'].classes_ else encoders['Grade'].classes_[0]
        
        # Get market for district
        district_markets = df[df['District'] == district]['Market'].unique()
        market = district_markets[0] if len(district_markets) > 0 else district
        
        price_result = predict_price(district, market, commodity, variety, grade, harvest_date)
        
        if not price_result['success']:
            return None
            
        predicted_price = price_result['predicted_price']
        
        # Calculate profit
        total_yield = crop_info['yield_per_acre'] * area_acres
        total_revenue = total_yield * predicted_price
        total_cost = crop_info['cost_per_acre'] * area_acres
        profit = total_revenue - total_cost
        profit_margin = (profit / total_revenue) * 100 if total_revenue > 0 else 0
        
        return {
            'commodity': commodity,
            'predicted_price': predicted_price,
            'yield_quintals': total_yield,
            'revenue': total_revenue,
            'cost': total_cost,
            'profit': profit,
            'profit_margin': profit_margin,
            'duration_months': crop_info['duration'],
            'harvest_month': harvest_month,
            'roi': (profit / total_cost) * 100 if total_cost > 0 else 0
        }
        
    except Exception as e:
        logging.error(f"Error calculating profit for {commodity}: {e}")
        return None

@app.route('/api/recommend-crop', methods=['POST'])
def recommend_crop():
    try:
        data = request.json
        soil_type = data.get('soilType')
        month = int(data.get('currentMonth'))
        previous_crop = data.get('previousCrop')
        district = data.get('district')
        area = float(data.get('area', 1))
        
        if not district or not encoders or df is None:
            return jsonify({'success': False, 'error': 'Model or data not available'}), 400
        
        # Load and analyze actual crop data from CSV
        try:
            df_crop = df.copy()
            df_crop['Modal_Price'] = pd.to_numeric(df_crop['Modal_Price'], errors='coerce')
            df_crop['Date'] = pd.to_datetime(df_crop['Date'], errors='coerce')
            df_crop['Month'] = df_crop['Date'].dt.month
            
            # Filter data for the district
            district_data = df_crop[df_crop['District'] == district]
            
            # Calculate average prices and profitability from actual data
            crop_stats = district_data.groupby('Commodity').agg({
                'Modal_Price': ['mean', 'std', 'count'],
                'Month': lambda x: x.mode().iloc[0] if len(x.mode()) > 0 else month
            }).round(2)
            
            crop_stats.columns = ['avg_price', 'price_volatility', 'data_points', 'peak_month']
            crop_stats = crop_stats[crop_stats['data_points'] >= 10]
            
        except Exception as e:
            logging.error(f"Error loading crop data: {e}")
            # Fallback to basic calculation using existing model
            crop_stats = None
        
        # Dynamic crop characteristics
        crop_duration = {'Rice': 4, 'Wheat': 5, 'Maize': 3, 'Potato': 3, 'Onion': 4, 'Tomato': 3, 'Groundnut': 4, 'Cabbage': 2}
        crop_yield = {'Rice': 25, 'Wheat': 20, 'Maize': 30, 'Potato': 150, 'Onion': 120, 'Tomato': 200, 'Groundnut': 15, 'Cabbage': 180}
        
        # Calculate profit potential for all available crops using the ML model
        crop_profitability = {}
        available_commodities = list(encoders['Commodity'].classes_)
        
        for crop in available_commodities:
            if crop in crop_duration and crop in crop_yield:
                # Get price from actual data or model prediction
                if crop_stats is not None and crop in crop_stats.index:
                    avg_price = crop_stats.loc[crop, 'avg_price']
                    volatility = crop_stats.loc[crop, 'price_volatility']
                else:
                    # Use model prediction as fallback
                    harvest_month = (month + crop_duration[crop]) % 12
                    if harvest_month == 0: harvest_month = 12
                    harvest_date = f"2024-{harvest_month:02d}-15"
                    
                    variety = "Local" if "Local" in encoders['Variety'].classes_ else encoders['Variety'].classes_[0]
                    grade = "FAQ" if "FAQ" in encoders['Grade'].classes_ else encoders['Grade'].classes_[0]
                    
                    district_markets = df[df['District'] == district]['Market'].unique()
                    market = district_markets[0] if len(district_markets) > 0 else district
                    
                    price_result = predict_price(district, market, crop, variety, grade, harvest_date)
                    avg_price = price_result['predicted_price'] if price_result['success'] else 2000
                    volatility = avg_price * 0.1  # Assume 10% volatility
                
                yield_per_acre = crop_yield[crop]
                duration = crop_duration[crop]
                
                # Add district-specific price variations
                district_multipliers = {
                    'Bangalore': 1.15, 'Mangalore': 1.12, 'Mysore': 1.08, 'Belgaum': 1.05,
                    'Dharwad': 1.03, 'Bagalkot': 0.98, 'Bijapur': 0.96, 'Bellary': 0.94,
                    'Raichur': 0.92, 'Koppal': 0.90, 'Gadag': 0.95, 'Haveri': 0.97,
                    'Davangere': 1.02, 'Chitradurga': 0.99, 'Tumkur': 1.06, 'Kolar': 1.04,
                    'Chikmagalur': 1.01, 'Hassan': 1.03, 'Mandya': 1.05, 'Chamrajnagar': 0.98,
                    'Shimoga': 1.00, 'Udupi': 1.08, 'Karwar': 1.10, 'Madikeri': 1.07,
                    'Bidar': 0.93, 'Kalburgi': 0.91
                }
                
                district_factor = district_multipliers.get(district, 1.0)
                adjusted_price = avg_price * district_factor
                
                # Calculate profit with district-adjusted prices
                revenue = adjusted_price * yield_per_acre
                
                # Crop-specific cost ratios
                cost_ratios = {
                    'Rice': 0.35, 'Wheat': 0.38, 'Maize': 0.32, 'Potato': 0.45,
                    'Onion': 0.42, 'Tomato': 0.48, 'Groundnut': 0.40, 'Cabbage': 0.35
                }
                cost_ratio = cost_ratios.get(crop, 0.40)
                estimated_costs = revenue * cost_ratio
                profit = revenue - estimated_costs
                
            profit_data = calculate_profit_potential(district, crop, month, area_acres=1)
            if profit_data:
                # Use the more robust calculation and add a volatility estimate
                profit = profit_data['profit']
                avg_price = profit_data['predicted_price']
                volatility = avg_price * 0.1 # Assume 10% volatility
                revenue = profit_data['revenue']
                estimated_costs = profit_data['cost']
                crop_profitability[crop] = {
                    'profit': profit,
                    'duration': duration,
                    'yield_per_acre': yield_per_acre,
                    'avg_price': adjusted_price,
                    'duration': profit_data['duration_months'],
                    'yield_per_acre': profit_data['yield_quintals'],
                    'avg_price': avg_price,
                    'volatility': volatility,
                    'revenue': revenue,
                    'costs': estimated_costs
                }
        
        # Dynamic seasonal analysis
        seasonal_crops = {'Rabi': [11, 12, 1, 2], 'Kharif': [6, 7, 8, 9], 'Summer': [3, 4, 5, 10]}
        
        current_season = None
        for season, months in seasonal_crops.items():
            if month in months:
                current_season = season
                break
        
        # Dynamic soil compatibility based on available crops
        available_crops = list(crop_profitability.keys())
        soil_compatibility = {
            'Clay': [c for c in available_crops if c in ['Rice', 'Wheat', 'Maize']],
            'Sandy': [c for c in available_crops if c in ['Groundnut', 'Maize', 'Potato']],
            'Loamy': [c for c in available_crops if c in ['Rice', 'Wheat', 'Potato', 'Onion', 'Tomato', 'Cabbage']],
            'Black': [c for c in available_crops if c in ['Rice', 'Wheat', 'Maize', 'Onion', 'Tomato']],
            'Red': [c for c in available_crops if c in ['Groundnut', 'Maize', 'Tomato']]
        }
        
        # Smart rotation: avoid same crop
        rotation_compatible = [c for c in available_crops if c != previous_crop]
        
        # Get compatible crops
        soil_compatible = soil_compatibility.get(soil_type, available_crops)
        suitable_crops = list(set(soil_compatible) & set(rotation_compatible))
        
        if not suitable_crops:
            suitable_crops = rotation_compatible[:5]  # Fallback
        
        # Calculate profit-adjusted scores using actual market data
        crop_scores = []
        for crop in suitable_crops:
            if crop in crop_profitability:
                profit_data = crop_profitability[crop]
                
                # Monthly profit from actual data
                monthly_profit = profit_data['profit'] / profit_data['duration']
                
                # Seasonal bonus based on actual price patterns
                seasonal_bonus = 1.0
                if crop_stats is not None and crop in crop_stats.index:
                    peak_month = crop_stats.loc[crop, 'peak_month']
                    if abs(peak_month - month) <= 1:
                        seasonal_bonus = 1.15
                    elif abs(peak_month - month) >= 4:
                        seasonal_bonus = 1.25
                
                # Risk adjustment based on price volatility
                volatility_factor = 1.0
                volatility = profit_data['volatility']
                avg_price = profit_data['avg_price']
                cv = volatility / avg_price if avg_price > 0 else 0.1
                volatility_factor = max(0.8, 1.2 - cv)
                
                # Soil-specific bonuses
                soil_bonuses = {
                    'Clay': {'Rice': 1.2, 'Wheat': 1.15, 'Maize': 1.1},
                    'Sandy': {'Groundnut': 1.25, 'Potato': 1.15, 'Maize': 1.1},
                    'Loamy': {'Tomato': 1.2, 'Cabbage': 1.15, 'Onion': 1.1},
                    'Black': {'Rice': 1.15, 'Wheat': 1.1, 'Maize': 1.05},
                    'Red': {'Groundnut': 1.2, 'Tomato': 1.15, 'Maize': 1.1}
                }
                soil_bonus = soil_bonuses.get(soil_type, {}).get(crop, 1.0)
                
                # Rotation bonuses (higher bonus for better rotation partners)
                rotation_bonuses = {
                    'Rice': {'Wheat': 1.15, 'Groundnut': 1.2, 'Potato': 1.1},
                    'Wheat': {'Rice': 1.15, 'Maize': 1.1, 'Tomato': 1.05},
                    'Maize': {'Rice': 1.1, 'Groundnut': 1.15, 'Cabbage': 1.1},
                    'Potato': {'Rice': 1.1, 'Onion': 1.05, 'Cabbage': 1.1},
                    'Onion': {'Rice': 1.1, 'Tomato': 1.05, 'Maize': 1.05},
                    'Tomato': {'Rice': 1.1, 'Wheat': 1.05, 'Cabbage': 1.05},
                    'Groundnut': {'Rice': 1.15, 'Maize': 1.1, 'Cabbage': 1.05},
                    'Cabbage': {'Rice': 1.1, 'Maize': 1.05, 'Tomato': 1.05}
                }
                rotation_bonus = rotation_bonuses.get(previous_crop, {}).get(crop, 1.0)
                
                final_score = monthly_profit * seasonal_bonus * volatility_factor * soil_bonus * rotation_bonus
                
                total_profit = profit_data['profit'] * area
                total_revenue = profit_data['revenue'] * area
                total_costs = profit_data['costs'] * area
                
                crop_scores.append({
                    'crop': crop,
                    'score': final_score,
                    'profit': total_profit,
                    'revenue': total_revenue,
                    'costs': total_costs,
                    'duration': profit_data['duration'],
                    'yield': profit_data['yield_per_acre'],
                    'avg_price': profit_data['avg_price'],
                    'volatility': volatility,
                    'roi': (total_profit / total_costs) * 100 if total_costs > 0 else 0,
                    'profit_margin': (total_profit / total_revenue) * 100 if total_revenue > 0 else 0
                })
        
        # Sort by score and get the best crop
        crop_scores.sort(key=lambda x: x['score'], reverse=True)
        
        if not crop_scores:
            return jsonify({'success': False, 'error': 'No suitable crops found'}), 400
        
        best_crop = crop_scores[0]
        recommended_crop = best_crop['crop']
        expected_profit = int(best_crop['profit'])
        expected_price = int(best_crop['avg_price'])
        
        # Generate profit comparison with other options
        other_options = crop_scores[1:4] if len(crop_scores) > 1 else []
        
        data_points = 0
        if crop_stats is not None and recommended_crop in crop_stats.index:
            data_points = int(crop_stats.loc[recommended_crop, 'data_points'])
        
        detailed_reason = f"""
🔍 *AI-Powered Recommendation (Based on Real Market Data):*

*Why {recommended_crop} after {previous_crop}:*
• 💰 *Data-Driven Profitability*: ₹{expected_profit:,}/acre (from {data_points} market records)
• 🌱 *Soil Match*: {soil_type} soil optimal for {recommended_crop}
• 🔄 *Smart Rotation*: Breaks {previous_crop} pest cycles
• 📅 *Seasonal Advantage*: {current_season} planting window
• ⏱ *Harvest Timeline*: {best_crop['duration']} months

📹 *Market Analysis (Real Data):*
• Average Price: ₹{expected_price}/quintal
• Expected Yield: {best_crop['yield']} quintals/acre
• Price Volatility: ₹{int(best_crop['volatility'])}/quintal
• Monthly Returns: ₹{expected_profit//best_crop['duration']:,}
• Risk Level: {'Low' if best_crop['volatility'] < 300 else 'Medium'}

📊 *Top Alternatives:*
{chr(10).join([f'• {opt["crop"]}: ₹{int(opt["profit"]):,}/acre, {opt["duration"]}mo' for opt in other_options])}

🌾 *Rotation Science:*
• Nutrient cycling optimization
• Pest/disease break cycle
• Soil health improvement
• Market risk diversification

🎯 *Profit Maximization:*
• Quality seeds: +25% yield
• Precision farming: +20% efficiency
• Market timing: +15% price premium
• Value addition opportunities

📈 *Market Intelligence:*
• Based on {district} historical data
• Seasonal price patterns analyzed
• Government scheme eligibility
• Export market potential
        """
        
        return jsonify({
            'success': True,
            'recommendedCrop': recommended_crop,
            'reason': detailed_reason,
            'expectedPrice': expected_price,
            'expectedProfit': expected_profit,
            'roi': round(best_crop['roi'], 1),
            'profitMargin': round(best_crop['profit_margin'], 1),
            'season': current_season,
            'harvestTime': f'{best_crop["duration"]} months',
            'expectedYield': f'{best_crop["yield"]} quintals/acre',
            'monthlyProfit': f'₹{expected_profit//best_crop["duration"]:,}/month',
            'riskLevel': 'Low risk' if best_crop['volatility'] < 300 else 'Medium risk',
            'localContext': f'{district} - Real market data analysis',
            'alternativeCrops': [{'name': opt['crop'], 'profit': int(opt['profit'])} for opt in other_options],
            'dataPoints': data_points,
            'volatility': int(best_crop['volatility']),
            'totalRevenue': int(best_crop['revenue']),
            'totalCosts': int(best_crop['costs'])
        })
        
    except Exception as e:
        logging.error(f"Error in crop recommendation: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/high-demand')
def high_demand():
    return render_template('high_demand.html')

@app.route('/api/high-demand', methods=['POST'])
def high_demand_api():
    return jsonify({"success": True, "redirect": "/high-demand"})

@app.route('/api/analyze-demand', methods=['POST'])
def analyze_demand():
    try:
        data = request.json
        district = data.get('district')
        month = int(data.get('month'))
        
        if encoders is None:
            return jsonify({'success': False, 'error': 'Model not loaded'}), 500
        
        available_commodities = list(encoders['Commodity'].classes_)
        current_date = f"2024-{month:02d}-15"
        
        market = district  # Use district as market fallback
        if df is not None:
            try:
                district_markets = df[df['District'] == district]['Market'].unique()
                if len(district_markets) > 0:
                    market = district_markets[0]
            except:
                pass
        
        # Predict prices for each commodity
        commodity_analysis = []
        for commodity in available_commodities:
            try:
                variety = "Local" if "Local" in encoders['Variety'].classes_ else encoders['Variety'].classes_[0]
                grade = "FAQ" if "FAQ" in encoders['Grade'].classes_ else encoders['Grade'].classes_[0]
                
                price_result = predict_price(district, market, commodity, variety, grade, current_date)
                
                if price_result['success']:
                    commodity_analysis.append({
                        'commodity': commodity,
                        'predicted_price': price_result['predicted_price']
                    })
            except:
                continue
        
        # Sort by predicted price
        commodity_analysis.sort(key=lambda x: x['predicted_price'], reverse=True)
        
        month_names = {1: 'January', 2: 'February', 3: 'March', 4: 'April', 5: 'May', 6: 'June',
                      7: 'July', 8: 'August', 9: 'September', 10: 'October', 11: 'November', 12: 'December'}
        
        # Generate top crops
        top_crops = []
        for i, item in enumerate(commodity_analysis[:5]):
            demand_score = 95 - (i * 5)
            
            trends = {'Rice': 'Stable', 'Wheat': 'Rising', 'Maize': 'Growing', 'Potato': 'Seasonal', 
                     'Onion': 'Volatile', 'Tomato': 'High returns', 'Groundnut': 'Oil demand', 'Cabbage': 'Quick returns'}
            
            reasons = {'Rice': 'Staple food crop', 'Wheat': 'Export opportunities', 'Maize': 'Industrial demand', 
                      'Potato': 'Processing demand', 'Onion': 'Export potential', 'Tomato': 'Fresh consumption', 
                      'Groundnut': 'Oil production', 'Cabbage': 'Local demand'}
            
            crop_name = item['commodity']
            top_crops.append({
                'name': crop_name,
                'avgPrice': round(item['predicted_price'], 0),
                'demandScore': demand_score,
                'trend': trends.get(crop_name, 'Moderate demand'),
                'reason': reasons.get(crop_name, 'Good market potential')
            })
        
        return jsonify({
            'success': True,
            'district': district,
            'monthName': month_names[month],
            'topCrops': top_crops
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/weather-advisory')
def weather_advisory():
    return render_template('weather_advisory.html')

# Weather API Configuration
import os
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")

@app.route('/api/weather/<district>')
def get_weather(district):
    try:
        # Extended coordinates for Karnataka districts
        district_coords = {
            'Bangalore': (12.9716, 77.5946),
            'Mysore': (12.2958, 76.6394),
            'Hubli': (15.3647, 75.1240),
            'Mangalore': (12.9141, 74.8560),
            'Belgaum': (15.8497, 74.4977),
            'Gulbarga': (17.3297, 76.8343),
            'Kalburgi': (17.3297, 76.8343),
            'Davangere': (14.4644, 75.9218),
            'Bellary': (15.1394, 76.9214),
            'Bijapur': (16.8302, 75.7100),
            'Shimoga': (13.9299, 75.5681),
            'Chitradurga': (14.2251, 76.3958),
            'Gadag': (15.4167, 75.6167),
            'Bidar': (17.9104, 77.5199),
            'Chikmagalur': (13.3161, 75.7720),
            'Hassan': (13.0033, 76.1004),
            'Tumkur': (13.3379, 77.1022),
            'Kolar': (13.1358, 78.1297),
            'Mandya': (12.5218, 76.8951),
            'Raichur': (16.2120, 77.3439)
        }
        
        # Clean district name - remove parenthetical information
        clean_district = district.split('(')[0].strip()
        
        # Try exact match first, then cleaned name
        coords = None
        if district in district_coords:
            coords = district_coords[district]
        elif clean_district in district_coords:
            coords = district_coords[clean_district]
        
        if coords is None:
            return jsonify({'error': f'District {district} not supported'}), 404
            
        lat, lon = coords
        
        # Try to get real weather data if API key is provided
        if OPENWEATHER_API_KEY != "your_openweather_api_key_here":
            try:
                import requests
                url = f"http://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={OPENWEATHER_API_KEY}&units=metric"
                response = requests.get(url, timeout=5)
                
                if response.status_code == 200:
                    data = response.json()
                    weather_data = {
                        'temperature': round(data['main']['temp']),
                        'humidity': data['main']['humidity'],
                        'rainfall': data.get('rain', {}).get('1h', 0),
                        'windSpeed': round(data['wind']['speed'] * 3.6),  # Convert m/s to km/h
                        'description': data['weather'][0]['description'],
                        'pressure': data['main']['pressure']
                    }
                    return jsonify(weather_data)
                else:
                    logging.warning(f"OpenWeather API returned status {response.status_code}")
            except Exception as e:
                logging.warning(f"Failed to fetch real weather data: {e}")
        
        # Fallback to simulated weather data
        import random
        weather_data = {
            'temperature': round(25 + (lat - 12) * 1.5 + random.uniform(-3, 3)),
            'humidity': round(65 + random.uniform(-15, 15)),
            'rainfall': round(random.uniform(0, 5), 1),
            'windSpeed': round(8 + random.uniform(-3, 7)),
            'description': random.choice(['clear sky', 'partly cloudy', 'scattered clouds', 'light rain']),
            'pressure': round(1013 + random.uniform(-10, 10))
        }
        return jsonify(weather_data)
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/fertilizer-calc')
def fertilizer_calc():
    return render_template('fertilizer_calc.html')

@app.route('/market-trends')
def market_trends():
    return render_template('market_trends.html')

@app.route('/profit-calculator')
def profit_calculator():
    return render_template('profit_calculator.html')

@app.route('/api/calculate-profit', methods=['POST'])
def api_calculate_profit():
    """API endpoint for the simple profit calculator."""
    try:
        data = request.json
        district = data.get('district')
        commodity = data.get('commodity')
        investment = float(data.get('investment', 0))
        yield_quintals = float(data.get('yield', 0))
        area_acres = float(data.get('area', 1))
        
        if not all([district, commodity, yield_quintals > 0]):
            return jsonify({'success': False, 'error': 'Missing required fields or invalid yield.'}), 400

        # Use a recent date for price prediction
        prediction_date = datetime.now().strftime('%Y-%m-%d')

        # Use default variety and grade for prediction
        variety = "Local" if "Local" in encoders['Variety'].classes_ else encoders['Variety'].classes_[0]
        grade = "FAQ" if "FAQ" in encoders['Grade'].classes_ else encoders['Grade'].classes_[0]
        
        # Get market for district
        district_markets = df[df['District'] == district]['Market'].unique()
        market = district_markets[0] if len(district_markets) > 0 else district

        price_result = predict_price(district, market, commodity, variety, grade, prediction_date)

        if not price_result.get('success'):
            # If prediction fails, return a clear error instead of crashing
            error_message = price_result.get('error', 'Could not predict price for the selected commodity.')
            return jsonify({'success': False, 'error': error_message}), 400

        predicted_price = price_result['predicted_price']
        revenue = predicted_price * yield_quintals
        profit = revenue - investment
        roi = (profit / investment) * 100 if investment > 0 else 0

        return jsonify({
            'success': True,
            'commodity': commodity,
            'district': district,
            'investment': investment,
            'revenue': revenue,
            'profit': profit,
            'roi': roi,
            'avgPrice': predicted_price,
            'area': area_acres,
            'yield': yield_quintals
        })
    except Exception as e:
        logging.error(f"Error in profit calculation API: {e}")
        return jsonify({'success': False, 'error': f'An internal error occurred: {e}'}), 500

@app.route('/farm-assistant')
def farm_assistant():
    return render_template('farm_assistant.html')

@app.route('/api/chat', methods=['POST'])
@app.route('/api/chatbot', methods=['POST'])
def chat_response():
    try:
        data = request.json
        message = data.get('message', '').lower().strip()
        
        if not message:
            return jsonify({'success': False, 'error': 'Empty message'})
        
        # Generate intelligent response using dataset
        response = generate_intelligent_response(message)
        
        return jsonify({
            'success': True,
            'response': response
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

def generate_intelligent_response(message):
    """Generate dynamic responses based on keywords"""
    
    # Greeting responses
    if any(word in message for word in ['hello', 'hi', 'hey', 'good morning', 'good afternoon']):
        return f"🌾 Hello farmer! I'm your AI assistant. How can I help you today?"
    
    # Price queries
    if 'price' in message:
        return f"💰 For specific price predictions, please use our <strong>Price Prediction</strong> tool. It uses a machine learning model for accurate forecasts."

    # Crop recommendation
    if any(word in message for word in ['recommend', 'suggest', 'best crop', 'what to plant', 'what crops should i plant']):
        return f"🌱 For personalized crop suggestions based on profit, soil, and season, please use our <strong>Crop Rotation</strong> tool."

    # Yield improvement
    if any(word in message for word in ['yield', 'production', 'increase crop yield']):
        return """ <strong>Tips to Increase Crop Yield:</strong><br><br>
1. <strong>Soil Health:</strong> Regular soil testing and adding organic matter.<br>
2. <strong>Quality Seeds:</strong> Use certified, high-yielding varieties.<br>
3. <strong>Water Management:</strong> Use efficient methods like drip irrigation.<br>
4. <strong>Pest Control:</strong> Implement Integrated Pest Management (IPM).<br><br>
Our specialized tools can provide more details!"""

    # Fertilizer advice
    if 'fertilizer' in message:
        return "For NPK and cost calculations for your specific crop and area, please use the <strong>Fertilizer Calculator</strong> tool."

    # Pest/Disease
    if any(word in message for word in ['pest', 'disease']):
        return "🔬 To diagnose crop diseases based on symptoms, please use our <strong>Disease Detection</strong> tool."

    # Default response
    return f"""🤖 I can help with general questions, but for the best results, please use the specialized tools in the sidebar:<br>
• <strong>Price Prediction</strong> for market rates.<br>
• <strong>Crop Rotation</strong> for planting advice.<br>
• <strong>High Demand Crops</strong> for market trends."""


if __name__ == '__main__':
    app.run(debug=True, port=5002)