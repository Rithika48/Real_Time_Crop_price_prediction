# Weather API Integration Setup

## Steps to Enable Real Weather Data:

1. **Get OpenWeatherMap API Key:**
   - Visit: https://openweathermap.org/api
   - Sign up for free account
   - Get your API key from dashboard

2. **Update API Key:**
   - Open `app.py`
   - Find line: `API_KEY = "your_openweather_api_key_here"`
   - Replace with your actual API key

3. **Test the Integration:**
   - Run the Flask app: `python app.py`
   - Go to Weather Advisory page
   - Select a district and check weather

## Features Added:
- Real-time weather data for Karnataka districts
- Temperature, humidity, rainfall, wind speed
- Weather description (sunny, cloudy, etc.)
- Intelligent farming advisory based on actual conditions

## Supported Districts:
- Bangalore, Mysore, Hubli, Mangalore, Belgaum
- Gulbarga, Davangere, Bellary, Bijapur, Shimoga
