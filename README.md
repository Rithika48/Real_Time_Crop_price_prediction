# Real-Time Crop Price Prediction & Smart Farming Insights
An AI-powered agricultural analytics system that leverages web scraping, historical price data, and weather insights to predict real-time crop prices. Along with accurate forecasting, it offers crop rotation recommendations and smart decision-support tools to promote sustainable and profitable farming.
The system uses **Machine Learning, agricultural datasets, and weather analytics** to predict crop prices and provide smart farming recommendations.

# Project Description

This project is a **web-based machine learning platform** that predicts agricultural crop prices and provides various tools to support smart farming practices.

The application analyzes historical market price data and uses a trained **XGBoost regression model** to estimate future crop prices.

Along with price prediction, the platform offers several intelligent modules such as:

- Crop Price Prediction  
- Crop Rotation Advisor  
- High Demand Crop Analysis  
- Weather Advisory System  
- Fertilizer Calculator  
- Disease Detection Assistant  
- Market Trend Analysis  
- Profit Calculator  

These modules help farmers understand market demand, crop profitability, and environmental factors before making farming decisions.

# ❗ Problem Statement

Agricultural markets are highly unpredictable due to multiple factors such as:

- Seasonal variations  
- Weather conditions  
- Supply and demand fluctuations  
- Lack of access to real-time market insights  

Many farmers do not have access to advanced tools that can help them forecast crop prices or analyze market trends.

This project aims to solve this problem by developing a **machine learning-based agricultural advisory system** that predicts crop prices and provides farming recommendations using historical data and analytics.

# 🛠 Tech Stack

### Programming Languages
- Python
- HTML
- CSS
- JavaScript

### Backend
- Flask

### Machine Learning
- XGBoost
- Scikit-learn

### Data Processing
- Pandas
- NumPy

### Data Storage
- CSV files

### APIs
- OpenWeatherMap API

### Visualization
- Chart.js

### Web Scraping
- BeautifulSoup
- Requests

# 📊 Dataset

The model is trained using **historical agricultural market price data** collected from government agricultural sources.

The dataset contains fields such as:

- District
- Market
- Commodity
- Variety
- Grade
- Arrival Date
- Modal Price

### Example Dataset Format

| District | Market | Commodity | Variety | Grade | Date | Modal Price |
|--------|--------|--------|--------|--------|--------|--------|
| Bangalore | Yeshwantpur | Rice | Basmati | FAQ | 15-01-2024 | 2500 |
| Mysore | Mysore Market | Wheat | Local | FAQ | 16-01-2024 | 2200 |

The dataset contains **multiple years of agricultural market data**, allowing the model to learn seasonal and geographical price patterns.

# ⚙️ How to Run

### 1. Clone the Repository

```bash
git clone https://github.com/Rithika48/Real_Time_Crop-price-prediction.git

### 2. Navigate to the Folder

cd crop-price-prediction

### 3. Install Dependencies

pip install -r requirements.txt

### 4. Run the Application

python app.py

### 5. Open in Browser

http://localhost:5001



