
import requests
import time
from flask import Flask, jsonify, request
import threading
from collections import deque
from flask_cors import CORS
app = Flask(__name__)

CORS(app)

# Initialize a dictionary of deques to store the latest 5 prices for each symbol
market_data = {
   "BTCUSDm": deque(maxlen=1),
  "EURUSDm": deque(maxlen=1),
  "GBPUSDm": deque(maxlen=1),
  "USDJPYm": deque(maxlen=1),
  "AUDUSDm": deque(maxlen=1),
  "ETHUSDm": deque(maxlen=1),
  "CADJPYm": deque(maxlen=1),
  "EURUSDm": deque(maxlen=1),
  "GBPCADm": deque(maxlen=1),
  "USDCADm": deque(maxlen=1),
  "AUDCADm": deque(maxlen=1),
  "GBPAUDm": deque(maxlen=1),
  "GBPJPYm": deque(maxlen=1),
  "USDJPYm": deque(maxlen=1),
  "EURGBPm": deque(maxlen=1),
  "EURJPYm": deque(maxlen=1),
}

# Function to fetch current price for a given symbol
def fetch_current_price(auth_token, symbol):
    url = f"https://mt-client-api-v1.london.agiliumtrade.ai/users/current/accounts/214e3d5c-32e2-476b-a15a-578d139ddb38/symbols/{symbol}/current-price"
    headers = {
        "Accept": "application/json",
        "auth-token": auth_token
    }
    
    try:
        response = requests.get(url, headers=headers)
        
        if response.status_code == 429:  # Handle rate limiting error
            print(f"Rate limit exceeded for {symbol}. Waiting for 60 seconds...")
            time.sleep(60)  # Wait for 60 seconds before retrying
            return fetch_current_price(auth_token, symbol)  # Retry the request
        
        response.raise_for_status()  # Raise an error for HTTP status codes 4xx/5xx
        return response.json()
    
    except requests.exceptions.RequestException as e:
        print(f"An error occurred for {symbol}: {e}")
        return None

# Function to update the prices for all symbols every second
def update_prices():
    auth_token =  "eyJhbGciOiJSUzUxMiIsInR5cCI6IkpXVCJ9.eyJfaWQiOiJjZmQwOTJkY2JiNWNjYzRiYmZiYjJiMmExN2VmMzFkNiIsInBlcm1pc3Npb25zIjpbXSwiYWNjZXNzUnVsZXMiOlt7ImlkIjoidHJhZGluZy1hY2NvdW50LW1hbmFnZW1lbnQtYXBpIiwibWV0aG9kcyI6WyJ0cmFkaW5nLWFjY291bnQtbWFuYWdlbWVudC1hcGk6cmVzdDpwdWJsaWM6KjoqIl0sInJvbGVzIjpbInJlYWRlciIsIndyaXRlciJdLCJyZXNvdXJjZXMiOlsiKjokVVNFUl9JRCQ6KiJdfSx7ImlkIjoibWV0YWFwaS1yZXN0LWFwaSIsIm1ldGhvZHMiOlsibWV0YWFwaS1hcGk6cmVzdDpwdWJsaWM6KjoqIl0sInJvbGVzIjpbInJlYWRlciIsIndyaXRlciJdLCJyZXNvdXJjZXMiOlsiKjokVVNFUl9JRCQ6KiJdfSx7ImlkIjoibWV0YWFwaS1ycGMtYXBpIiwibWV0aG9kcyI6WyJtZXRhYXBpLWFwaTp3czpwdWJsaWM6KjoqIl0sInJvbGVzIjpbInJlYWRlciIsIndyaXRlciJdLCJyZXNvdXJjZXMiOlsiKjokVVNFUl9JRCQ6KiJdfSx7ImlkIjoibWV0YWFwaS1yZWFsLXRpbWUtc3RyZWFtaW5nLWFwaSIsIm1ldGhvZHMiOlsibWV0YWFwaS1hcGk6d3M6cHVibGljOio6KiJdLCJyb2xlcyI6WyJyZWFkZXIiLCJ3cml0ZXIiXSwicmVzb3VyY2VzIjpbIio6JFVTRVJfSUQkOioiXX0seyJpZCI6Im1ldGFzdGF0cy1hcGkiLCJtZXRob2RzIjpbIm1ldGFzdGF0cy1hcGk6cmVzdDpwdWJsaWM6KjoqIl0sInJvbGVzIjpbInJlYWRlciIsIndyaXRlciJdLCJyZXNvdXJjZXMiOlsiKjokVVNFUl9JRCQ6KiJdfSx7ImlkIjoicmlzay1tYW5hZ2VtZW50LWFwaSIsIm1ldGhvZHMiOlsicmlzay1tYW5hZ2VtZW50LWFwaTpyZXN0OnB1YmxpYzoqOioiXSwicm9sZXMiOlsicmVhZGVyIiwid3JpdGVyIl0sInJlc291cmNlcyI6WyIqOiRVU0VSX0lEJDoqIl19LHsiaWQiOiJjb3B5ZmFjdG9yeS1hcGkiLCJtZXRob2RzIjpbImNvcHlmYWN0b3J5LWFwaTpyZXN0OnB1YmxpYzoqOioiXSwicm9sZXMiOlsicmVhZGVyIiwid3JpdGVyIl0sInJlc291cmNlcyI6WyIqOiRVU0VSX0lEJDoqIl19LHsiaWQiOiJtdC1tYW5hZ2VyLWFwaSIsIm1ldGhvZHMiOlsibXQtbWFuYWdlci1hcGk6cmVzdDpkZWFsaW5nOio6KiIsIm10LW1hbmFnZXItYXBpOnJlc3Q6cHVibGljOio6KiJdLCJyb2xlcyI6WyJyZWFkZXIiLCJ3cml0ZXIiXSwicmVzb3VyY2VzIjpbIio6JFVTRVJfSUQkOioiXX0seyJpZCI6ImJpbGxpbmctYXBpIiwibWV0aG9kcyI6WyJiaWxsaW5nLWFwaTpyZXN0OnB1YmxpYzoqOioiXSwicm9sZXMiOlsicmVhZGVyIl0sInJlc291cmNlcyI6WyIqOiRVU0VSX0lEJDoqIl19XSwiaWdub3JlUmF0ZUxpbWl0cyI6ZmFsc2UsInRva2VuSWQiOiIyMDIxMDIxMyIsImltcGVyc29uYXRlZCI6ZmFsc2UsInJlYWxVc2VySWQiOiJjZmQwOTJkY2JiNWNjYzRiYmZiYjJiMmExN2VmMzFkNiIsImlhdCI6MTczNjA2MDczMiwiZXhwIjoxNzQzODM2NzMyfQ.Atjq5OqUrXJ1ItUXw5n_sQ5NWaf1gYh_EMhi8zLcwGQOtx2JgWEcZHhR1LxQNJxcRKMiqSkIA3TQ8A9PgB0wZ8VyCCDIlNe-RyyBrc5OWbuJE3YkTcvzgZn1BiAJGEPhCyfS26vBdJWm88MSb90stchZInvoLDe_MHb8c7nFKxuPYCOvu6ph_zUV3FTN67xZ_czP2NWrqbstiFv1-Zmhpfnlwm48Onq6qTmPbTPdIqz2r83UXHiyXOpewTJ2rlcdXe5hui1E0Y2ZJ0ufiunRsfvkQ4KGzAg0-kpoS6VoS-DDasfxcW6RK99M0XDQzuG3-SYsanH1EkbPs8tGqMWmMr0YatuxhmoiJu2FrQbp4VCziEiOBDtVLpUpyuAk5t3lxMuhZbcyXKF-If3qCSR3PPl-Xm_VJ4o3eFWtlqjz30HNnHCujP8ETW5AeNPet8ZIuR2ML9z9APLiWmF5fUYQUm6sGbt7lIF2laO3mWSFYWtPsrZlj--micjElUUrt4_UuEiPUKIXqwOFaZSsCiD3AIQPpgh1PoZr0vVBAkh4IooY85leSz7J7Y15lDJ8M7yHWsJu3GZRjWVDLmnB6P6tdRTgXUR94yJAAvJaFZ3JM02AbNjwKNbdM4jHL2Ce-LNuS3Kk99loiRWp9skR2SW8nWiseAmQOBDLIo_lgfFeoKs"  # Replace with your actual auth token
    
    while True:
        for symbol in market_data.keys():
            print(f"Fetching current price for {symbol}...")
            data = fetch_current_price(auth_token, symbol)
            
            if data:
                # Add the latest price to the deque for the symbol
                market_data[symbol].append(data)
                print(f"Updated best 5 prices for {symbol}: {list(market_data[symbol])}")
            else:
                print(f"Failed to fetch the current price for {symbol}.")
        
        time.sleep(1)  # Wait for 1 second before fetching again

# Route to fetch the best 5 prices for all symbols or a specific symbol
@app.route('/market-data', methods=['GET'])
def get_market_data():
    symbol = request.args.get('symbol')
    
    if symbol:
        symbol = symbol.upper()
        if symbol in market_data:
            return jsonify(list(market_data[symbol]))
        else:
            return jsonify({"error": f"No data available for symbol {symbol}"}), 400
    else:
        # Return the best 5 prices for all symbols
        return jsonify({sym: list(prices) for sym, prices in market_data.items()})


# Long polling endpoint
@app.route('/stream-market-data', methods=['GET'])
def stream_market_data():
    symbol = request.args.get('symbol')
    
    if symbol:
        symbol = symbol.upper()
        if symbol not in market_data:
            return jsonify({"error": f"No data available for symbol {symbol}"}), 400
        
        # Wait until new data is available or timeout
        timeout = time.time() + 30  # 30 seconds timeout
        while time.time() < timeout:
            if len(market_data[symbol]) > 0:
                return jsonify(list(market_data[symbol]))
            time.sleep(1)  # Check again in 1 second
        
        return jsonify({"error": "No new market data available"}), 408  # Timeout error
    
    else:
        return jsonify({"error": "Symbol parameter is required"}), 400

# Start the background thread to continuously fetch the prices
if __name__ == "__main__":
    # Start the price update in a separate thread
    threading.Thread(target=update_prices, daemon=True).start()
    
    # Run the Flask web server on localhost at port 5000
    app.run(debug=True, host='0.0.0.0', port=8080)
