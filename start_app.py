import subprocess
import webbrowser
import time
import os

def start_app():
    print("Starting Crop Price Prediction System...")
    
    # Start Flask app
    try:
        process = subprocess.Popen(['python', 'app_fixed.py'], cwd=os.getcwd())
        
        # Wait for server to start
        time.sleep(3)
        
        # Open browser
        webbrowser.open('http://localhost:5000')
        
        print("App started successfully!")
        print("Access the application at: http://localhost:5000")
        print("Press Ctrl+C to stop the server")
        
        # Keep the process running
        process.wait()
        
    except KeyboardInterrupt:
        print("\nShutting down...")
        process.terminate()
    except Exception as e:
        print(f"Error starting app: {e}")

if __name__ == "__main__":
    start_app()