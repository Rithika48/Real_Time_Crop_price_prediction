#!/usr/bin/env python3
"""
Weather API Setup Helper
This script helps you set up the OpenWeatherMap API for real weather data.
"""

import requests
import json

def test_weather_api(api_key):
    """Test if the provided API key works"""
    # Test with Bangalore coordinates
    lat, lon = 12.9716, 77.5946
    url = f"http://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={api_key}&units=metric"
    
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            print("✅ API Key is working!")
            print(f"Current weather in Bangalore:")
            print(f"Temperature: {data['main']['temp']}°C")
            print(f"Humidity: {data['main']['humidity']}%")
            print(f"Description: {data['weather'][0]['description']}")
            return True
        else:
            print(f"❌ API Error: {response.status_code}")
            print(f"Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Connection Error: {e}")
        return False

def update_app_with_api_key(api_key):
    """Update app.py with the provided API key"""
    try:
        with open('app.py', 'r') as f:
            content = f.read()
        
        # Replace the placeholder API key
        updated_content = content.replace(
            'OPENWEATHER_API_KEY = "your_openweather_api_key_here"',
            f'OPENWEATHER_API_KEY = "{api_key}"'
        )
        
        with open('app.py', 'w') as f:
            f.write(updated_content)
        
        print("✅ API key updated in app.py")
        return True
    except Exception as e:
        print(f"❌ Error updating app.py: {e}")
        return False

def main():
    print("🌤️  Weather API Setup Helper")
    print("=" * 40)
    
    print("\n📋 Steps to get your free API key:")
    print("1. Go to: https://openweathermap.org/api")
    print("2. Click 'Sign Up' (it's free!)")
    print("3. Verify your email")
    print("4. Go to API Keys section in your dashboard")
    print("5. Copy your API key")
    
    print("\n" + "=" * 40)
    api_key = input("Enter your OpenWeatherMap API key: ").strip()
    
    if not api_key:
        print("❌ No API key provided!")
        return
    
    print("\n🧪 Testing API key...")
    if test_weather_api(api_key):
        print("\n📝 Updating app.py...")
        if update_app_with_api_key(api_key):
            print("\n🎉 Setup complete!")
            print("Your weather API is now ready to use.")
            print("Restart your Flask app to see real weather data.")
        else:
            print("\n⚠️  API key works but couldn't update app.py")
            print(f"Please manually replace 'your_openweather_api_key_here' with '{api_key}' in app.py")
    else:
        print("\n❌ API key test failed. Please check your key and try again.")

if __name__ == "__main__":
    main()
