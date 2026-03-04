from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/api/weather/<district>')
def get_weather(district):
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
    
    if district not in district_coords:
        return jsonify({'error': f'District {district} not supported'}), 404
        
    lat, lon = district_coords[district]
    
    # Return simulated data
    weather_data = {
        'temperature': int(25 + (lat - 12) * 2),
        'humidity': 70,
        'rainfall': 0,
        'windSpeed': 10,
        'description': 'partly cloudy',
        'pressure': 1013
    }
    return jsonify(weather_data)

if __name__ == '__main__':
    app.run(debug=True, port=5001)
