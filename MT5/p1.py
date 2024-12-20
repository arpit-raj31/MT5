import requests
import time
from flask import Flask, jsonify
import threading
from collections import deque

app = Flask(__name__)

# Initialize a dictionary of deques to store the latest 5 prices for each symbol
market_data = {
    "XAUUSDm": deque(maxlen=5),
    "EURUSDm": deque(maxlen=5),
    "GBPUSDm": deque(maxlen=5),
    "USDJPYm": deque(maxlen=5),
    "AUDUSDm": deque(maxlen=5)
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
    auth_token = "eyJhbGciOiJSUzUxMiIsInR5cCI6IkpXVCJ9.eyJfaWQiOiJjZmQwOTJkY2JiNWNjYzRiYmZiYjJiMmExN2VmMzFkNiIsInBlcm1pc3Npb25zIjpbXSwiYWNjZXNzUnVsZXMiOlt7ImlkIjoidHJhZGluZy1hY2NvdW50LW1hbmFnZW1lbnQtYXBpIiwibWV0aG9kcyI6WyJ0cmFkaW5nLWFjY291bnQtbWFuYWdlbWVudC1hcGk6cmVzdDpwdWJsaWM6KjoqIl0sInJvbGVzIjpbInJlYWRlciIsIndyaXRlciJdLCJyZXNvdXJjZXMiOlsiKjokVVNFUl9JRCQ6KiJdfSx7ImlkIjoibWV0YWFwaS1yZXN0LWFwaSIsIm1ldGhvZHMiOlsibWV0YWFwaS1hcGk6cmVzdDpwdWJsaWM6KjoqIl0sInJvbGVzIjpbInJlYWRlciIsIndyaXRlciJdLCJyZXNvdXJjZXMiOlsiKjokVVNFUl9JRCQ6KiJdfSx7ImlkIjoibWV0YWFwaS1ycGMtYXBpIiwibWV0aG9kcyI6WyJtZXRhYXBpLWFwaTp3czpwdWJsaWM6KjoqIl0sInJvbGVzIjpbInJlYWRlciIsIndyaXRlciJdLCJyZXNvdXJjZXMiOlsiKjokVVNFUl9JRCQ6KiJdfSx7ImlkIjoibWV0YWFwaS1yZWFsLXRpbWUtc3RyZWFtaW5nLWFwaSIsIm1ldGhvZHMiOlsibWV0YWFwaS1hcGk6d3M6cHVibGljOio6KiJdLCJyb2xlcyI6WyJyZWFkZXIiLCJ3cml0ZXIiXSwicmVzb3VyY2VzIjpbIio6JFVTRVJfSUQkOioiXX0seyJpZCI6Im1ldGFzdGF0cy1hcGkiLCJtZXRob2RzIjpbIm1ldGFzdGF0cy1hcGk6cmVzdDpwdWJsaWM6KjoqIl0sInJvbGVzIjpbInJlYWRlciIsIndyaXRlciJdLCJyZXNvdXJjZXMiOlsiKjokVVNFUl9JRCQ6KiJdfSx7ImlkIjoicmlzay1tYW5hZ2VtZW50LWFwaSIsIm1ldGhvZHMiOlsicmlzay1tYW5hZ2VtZW50LWFwaTpyZXN0OnB1YmxpYzoqOioiXSwicm9sZXMiOlsicmVhZGVyIiwid3JpdGVyIl0sInJlc291cmNlcyI6WyIqOiRVU0VSX0lEJDoqIl19LHsiaWQiOiJjb3B5ZmFjdG9yeS1hcGkiLCJtZXRob2RzIjpbImNvcHlmYWN0b3J5LWFwaTpyZXN0OnB1YmxpYzoqOioiXSwicm9sZXMiOlsicmVhZGVyIiwid3JpdGVyIl0sInJlc291cmNlcyI6WyIqOiRVU0VSX0lEJDoqIl19LHsiaWQiOiJtdC1tYW5hZ2VyLWFwaSIsIm1ldGhvZHMiOlsibXQtbWFuYWdlci1hcGk6cmVzdDpkZWFsaW5nOio6KiIsIm10LW1hbmFnZXItYXBpOnJlc3Q6cHVibGljOio6KiJdLCJyb2xlcyI6WyJyZWFkZXIiLCJ3cml0ZXIiXSwicmVzb3VyY2VzIjpbIio6JFVTRVJfSUQkOioiXX0seyJpZCI6ImJpbGxpbmctYXBpIiwibWV0aG9kcyI6WyJiaWxsaW5nLWFwaTpyZXN0OnB1YmxpYzoqOioiXSwicm9sZXMiOlsicmVhZGVyIl0sInJlc291cmNlcyI6WyIqOiRVU0VSX0lEJDoqIl19XSwiaWdub3JlUmF0ZUxpbWl0cyI6ZmFsc2UsInRva2VuSWQiOiIyMDIxMDIxMyIsImltcGVyc29uYXRlZCI6ZmFsc2UsInJlYWxVc2VySWQiOiJjZmQwOTJkY2JiNWNjYzRiYmZiYjJiMmExN2VmMzFkNiIsImlhdCI6MTczNDYwODM3NSwiZXhwIjoxNzQyMzg0Mzc1fQ.fCCzKSDvjAFtsv6UpAd68V4fsf9w1XzC7QRsxSys5aOH2JXK2lvihoPoR4cJ0TbzfEdIKmLVd3V6QFpOv2RoE1QO8iEJoK4F84a2yk3A9xuuwTMPT9_XaWk3T4AQ12o1gf_C1NM41g27CnK1vF765Dltvjyp_rzRzkbBbFeWg4JMmxM2TyxlXo24_8ZCxeiEEqjlww-HBYuC2G2YwMx2agAmIblbkLgVyzWimLPe86WUDbgYnMxuMfhNL2O1sHRR7vDPB2-4SW1sn1LNMqrmqKk-U91orbosQFGX5szOPN4wBGaQnS3NGwyXv3OWRDnxzz7TghW387n0Pj3T1l8nMfA4xtJLdRocN5v8RrtCOB0m8WgLGNzzoqVrV-esLLcyBOTnkBCXe7JqprIpEZ0NvNpz5rDstH1cH_uQpQ3XuLnGlsrRd6ArgCx7Ae3Ds6hvjJ7r_1y3V73oF8o9VcyYliDNo69O-E8Xv4P9YtMYxbCKNbZEoCKy7cvHVvu1fq_FC8BJONttltplHSPe6Z9CnjcWR7Gs2fAx1q-B04HxG-6mnO2Y4YMP2a_grLfxiujdFvWiS_BezLBUJawOrhshWE2VukKBdxtcPFPnvKGtNLm2tm9kvJhl1qDHPWFqraV4hhzBdyf5KmE8QyU5jqoGNjslWJ4c4aHJO9flnK9gmqU"  # Replace with your actual auth token
    
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
    symbol = requests.args.get('symbol')
    
    if symbol:
        symbol = symbol.upper()
        if symbol in market_data:
            return jsonify(list(market_data[symbol]))
        else:
            return jsonify({"error": f"No data available for symbol {symbol}"}), 400
    else:
        # Return the best 5 prices for all symbols
        return jsonify({sym: list(prices) for sym, prices in market_data.items()})

# Start the background thread to continuously fetch the prices
if __name__ == "__main__":
    # Start the price update in a separate thread
    threading.Thread(target=update_prices, daemon=True).start()
    
    # Run the Flask web server on localhost at port 5000
    app.run(debug=True, host='0.0.0.0', port=5000)
