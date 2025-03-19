import requests
import time
from flask import Flask, jsonify, request
import threading
from collections import deque
from flask_cors import CORS
app = Flask(__name__)

CORS(app)

# Initialize a dictionary of deques to store the latest 5 prices for each symbol
from collections import deque

market_data = {
    # Major Pairs
    "EURUSDm": deque(maxlen=1),
    "USDJPYm": deque(maxlen=1),
    "GBPUSDm": deque(maxlen=1),
    "AUDUSDm": deque(maxlen=1),
    "USDCHFm": deque(maxlen=1),
    "USDCADm": deque(maxlen=1),
    "NZDUSDm": deque(maxlen=1),
    "EURGBPm": deque(maxlen=1),
    "EURJPYm": deque(maxlen=1),
    "GBPJPYm": deque(maxlen=1),
    "AUDJPYm": deque(maxlen=1),
    "CHFJPYm": deque(maxlen=1),
    "EURAUDm": deque(maxlen=1),
    "EURCHFm": deque(maxlen=1),
    "GBPCHFm": deque(maxlen=1),
    "GBPAUDm": deque(maxlen=1),
    "CADJPYm": deque(maxlen=1),
    "NZDJPYm": deque(maxlen=1),
    "AUDCADm": deque(maxlen=1),
    "AUDNZDm": deque(maxlen=1),
    "EURNZDm": deque(maxlen=1),
    "GBPCADm": deque(maxlen=1),
    "USDZARm": deque(maxlen=1),
    "USDMXNm": deque(maxlen=1),
    "USDTRYm": deque(maxlen=1),
    "USDSEKm": deque(maxlen=1),
    "USDNOKm": deque(maxlen=1),
    "USDSGDm": deque(maxlen=1),
    "USDCNHm": deque(maxlen=1),
    "EURTRYm": deque(maxlen=1),
    "EURSEKm": deque(maxlen=1),
    "EURNOKm": deque(maxlen=1),
    "EURPLNm": deque(maxlen=1),
    "GBPTRYm": deque(maxlen=1),
    "GBPZARm": deque(maxlen=1),
    "BTCUSDm": deque(maxlen=1),
    "ETHUSDm": deque(maxlen=1),
    "LTCUSDm": deque(maxlen=1),
    "XRPUSDm": deque(maxlen=1),
    "USDINRm": deque(maxlen=1),
    "USDCADm": deque(maxlen=1),
}

def fetch_current_price(auth_token, symbol):
    url = f"https://mt-client-api-v1.london.agiliumtrade.ai/users/current/accounts/05bebca6-8b1f-4bed-8120-0874d639a279/symbols/{symbol}/current-price"
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
    auth_token =  "eyJhbGciOiJSUzUxMiIsInR5cCI6IkpXVCJ9.eyJfaWQiOiJjZmQwOTJkY2JiNWNjYzRiYmZiYjJiMmExN2VmMzFkNiIsImFjY2Vzc1J1bGVzIjpbeyJpZCI6InRyYWRpbmctYWNjb3VudC1tYW5hZ2VtZW50LWFwaSIsIm1ldGhvZHMiOlsidHJhZGluZy1hY2NvdW50LW1hbmFnZW1lbnQtYXBpOnJlc3Q6cHVibGljOio6KiJdLCJyb2xlcyI6WyJyZWFkZXIiXSwicmVzb3VyY2VzIjpbImFjY291bnQ6JFVTRVJfSUQkOjA1YmViY2E2LThiMWYtNGJlZC04MTIwLTA4NzRkNjM5YTI3OSJdfSx7ImlkIjoibWV0YWFwaS1yZXN0LWFwaSIsIm1ldGhvZHMiOlsibWV0YWFwaS1hcGk6cmVzdDpwdWJsaWM6KjoqIl0sInJvbGVzIjpbInJlYWRlciIsIndyaXRlciJdLCJyZXNvdXJjZXMiOlsiYWNjb3VudDokVVNFUl9JRCQ6MDViZWJjYTYtOGIxZi00YmVkLTgxMjAtMDg3NGQ2MzlhMjc5Il19LHsiaWQiOiJtZXRhYXBpLXJwYy1hcGkiLCJtZXRob2RzIjpbIm1ldGFhcGktYXBpOndzOnB1YmxpYzoqOioiXSwicm9sZXMiOlsicmVhZGVyIiwid3JpdGVyIl0sInJlc291cmNlcyI6WyJhY2NvdW50OiRVU0VSX0lEJDowNWJlYmNhNi04YjFmLTRiZWQtODEyMC0wODc0ZDYzOWEyNzkiXX0seyJpZCI6Im1ldGFhcGktcmVhbC10aW1lLXN0cmVhbWluZy1hcGkiLCJtZXRob2RzIjpbIm1ldGFhcGktYXBpOndzOnB1YmxpYzoqOioiXSwicm9sZXMiOlsicmVhZGVyIiwid3JpdGVyIl0sInJlc291cmNlcyI6WyJhY2NvdW50OiRVU0VSX0lEJDowNWJlYmNhNi04YjFmLTRiZWQtODEyMC0wODc0ZDYzOWEyNzkiXX0seyJpZCI6Im1ldGFzdGF0cy1hcGkiLCJtZXRob2RzIjpbIm1ldGFzdGF0cy1hcGk6cmVzdDpwdWJsaWM6KjoqIl0sInJvbGVzIjpbInJlYWRlciJdLCJyZXNvdXJjZXMiOlsiYWNjb3VudDokVVNFUl9JRCQ6MDViZWJjYTYtOGIxZi00YmVkLTgxMjAtMDg3NGQ2MzlhMjc5Il19LHsiaWQiOiJyaXNrLW1hbmFnZW1lbnQtYXBpIiwibWV0aG9kcyI6WyJyaXNrLW1hbmFnZW1lbnQtYXBpOnJlc3Q6cHVibGljOio6KiJdLCJyb2xlcyI6WyJyZWFkZXIiXSwicmVzb3VyY2VzIjpbImFjY291bnQ6JFVTRVJfSUQkOjA1YmViY2E2LThiMWYtNGJlZC04MTIwLTA4NzRkNjM5YTI3OSJdfV0sImlnbm9yZVJhdGVMaW1pdHMiOmZhbHNlLCJ0b2tlbklkIjoiMjAyMTAyMTMiLCJpbXBlcnNvbmF0ZWQiOmZhbHNlLCJyZWFsVXNlcklkIjoiY2ZkMDkyZGNiYjVjY2M0YmJmYmIyYjJhMTdlZjMxZDYiLCJpYXQiOjE3NDIzODA5MTIsImV4cCI6MTc1MDE1NjkxMn0.aOeAF3SJfXQkjmOh0sbGxK0OMmTD4rSqzXbiva2ljDAVEi6zaLsiFL-sXLf2_uKtx3AMa4eYgILqY5n_FixsnSYBxV50iijLJttELQPQ3n65DMTqBzAo9f151TcNbYHP4U71_1VqcqSjYKqiq8vqwoYknuVrwByVVWN-bje7IZkGtMC4ruj-QabZh-4cpebahoTmAUkUh8L1aK0gwnyDwk-6PgyUsCiAXM62mtBsq6boYYGebFEenfLMTtgzWwI8nRWC_Eq6qFtagxWB_sZ_LO43npv9y8nxz1rf4G7LMlzxrqj--2ZkWEW5qBLp3JUQwxAhntjvx6YWRszwLDXXatALvtRxWyrHq3xF2aUic2hIoTUUHaFEn8SF4KLRAfD4P8GhhawWfUMatIHkyoGfW7v47jTGPfUCCjUPgaYHQqx7X0u7j5EOLmTYV8jeeJb7hvzXRxP-fvKQbbWzuuQO4m5EqtYFrez-VI0bYfUnmYI7leU9xbRYChu1ACkeWAzph2MABpNM-fKyWekyhaUA4kKQBFfhy7yz-bda7IlwwdVxBkYUo_Ec_6NiESFmXwDvJmZb7oPAoRc5ZHplSa5a9l0HleBCvKkVrwwKDLOD5lRETi475rKw58QDF_dHwmcUsQ0_pb2T-8od3zdLmqmu43nE7jYthLp_P7YwsQmSCQQ"  # Replace with your actual auth token
    
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
        
        time.sleep(0)  # Wait for 1 second before fetching again

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
        # Return the best prices for all symbols
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
    app.run(debug=True, host='0.0.0.0', port=8000)
