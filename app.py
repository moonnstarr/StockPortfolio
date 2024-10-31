import json
import yfinance as yf
from flask import Flask, render_template, request, redirect, url_for
from datetime import datetime
import os

app = Flask(__name__)

# File path for storing portfolio data
PORTFOLIO_FILE = os.path.join('data', 'portfolio.json')

def load_portfolio():
    """Load portfolio data from a JSON file."""
    try:
        with open(PORTFOLIO_FILE, 'r') as file:
            portfolio = json.load(file)
            # Convert purchase_date strings back to datetime objects
            for stock in portfolio["stocks"]:
                stock["purchase_date"] = datetime.strptime(stock["purchase_date"], '%Y-%m-%d')
            return portfolio
    except (FileNotFoundError, json.JSONDecodeError):
        # If the file is not found or contains invalid JSON, return a default portfolio
        return {
            "total_value": 0.0,
            "total_gain_loss": 0.0,
            "stocks": []
        }

def save_portfolio(portfolio):
    """Save portfolio data to a JSON file."""
    try:
        # Convert datetime objects to strings for JSON compatibility
        for stock in portfolio["stocks"]:
            stock["purchase_date"] = stock["purchase_date"].strftime('%Y-%m-%d')
        
        with open(PORTFOLIO_FILE, 'w') as file:
            json.dump(portfolio, file)
    except Exception as e:
        print(f"Error saving portfolio: {e}")

portfolio = load_portfolio()  # Load the initial portfolio

def fetch_current_price(symbol):
    try:
        stock = yf.Ticker(symbol)
        current_price = stock.history(period="1d")['Close'].iloc[-1]  # Get the last closing price
        return current_price
    except Exception as e:
        print(f"Error fetching price for {symbol}: {e}")
        return None

def fetch_dividend_yield(symbol):
    try:
        stock = yf.Ticker(symbol)
        dividend_yield = stock.info.get('dividendYield', 0.0)  # Get the dividend yield safely
        return (dividend_yield * 100) if dividend_yield is not None else 0.0  # Convert to percentage
    except Exception as e:
        print(f"Error fetching dividend yield for {symbol}: {e}")
        return 0.0

def calculate_capital_gain_percentage(purchase_price, current_price):
    """Calculate the capital gain percentage."""
    if purchase_price == 0:
        return 0.0
    return ((current_price - purchase_price) / purchase_price) * 100

def fetch_stock_metrics(symbol):
    """Fetch additional stock metrics including P/E Ratio, EPS, and Market Cap Category."""
    try:
        stock = yf.Ticker(symbol)
        pe_ratio = stock.info.get('trailingPE', 'N/A')  # P/E Ratio
        eps = stock.info.get('trailingEps', 'N/A')  # EPS
        market_cap = stock.info.get('marketCap', 0)  # Market Cap
        
        # Categorize Market Cap
        if market_cap >= 200e9:
            market_cap_category = "Large Cap"
        elif 10e9 <= market_cap < 200e9:
            market_cap_category = "Mid Cap"
        elif 2e9 <= market_cap < 10e9:
            market_cap_category = "Small Cap"
        else:
            market_cap_category = "Micro Cap"

        return pe_ratio, eps, market_cap_category
    except Exception as e:
        print(f"Error fetching metrics for {symbol}: {e}")
        return 'N/A', 'N/A', 'Unknown'

def update_portfolio():
    # Update total value, total gain/loss, dividend yield, and capital gain percentage
    for stock in portfolio["stocks"]:
        current_price = fetch_current_price(stock['symbol'])
        dividend_yield = fetch_dividend_yield(stock['symbol'])
        
        if current_price is not None:
            stock['current_price'] = current_price
            stock['gain_loss'] = (current_price - stock['purchase_price']) * stock['quantity']
            stock['total_value'] = current_price * stock['quantity']
            stock['dividend_yield'] = dividend_yield  # Store dividend yield
            stock['capital_gain_percentage'] = calculate_capital_gain_percentage(stock['purchase_price'], current_price)  # Calculate capital gain percentage
        else:
            stock['current_price'] = stock['purchase_price']  # Fallback to purchase price if fetch fails

    portfolio["total_value"] = sum(stock['total_value'] for stock in portfolio["stocks"])
    portfolio["total_gain_loss"] = sum(stock['gain_loss'] for stock in portfolio["stocks"])

@app.route('/')
def index():
    update_portfolio()  # Update portfolio values before rendering
    save_portfolio(portfolio)  # Save updated portfolio after refreshing
    return render_template('index.html', portfolio=portfolio)

@app.route('/add_stock', methods=['POST'])
def add_stock():
    symbol = request.form['symbol']
    quantity = int(request.form['quantity'])
    purchase_price = float(request.form['purchase_price'])
    purchase_date = request.form['purchase_date']  # Get the purchase date from the form

    # Fetch current price, dividend yield, and additional metrics for the newly added stock
    current_price = fetch_current_price(symbol)
    dividend_yield = fetch_dividend_yield(symbol)
    pe_ratio, eps, market_cap_category = fetch_stock_metrics(symbol)  # Fetch additional metrics

    if current_price is None:
        current_price = purchase_price  # Default to purchase price if API fails

    # Calculate gain/loss and capital gain percentage
    gain_loss = (current_price - purchase_price) * quantity
    capital_gain_percentage = calculate_capital_gain_percentage(purchase_price, current_price)

    # Add stock to portfolio
    portfolio["stocks"].append({
        "symbol": symbol,
        "quantity": quantity,
        "purchase_price": purchase_price,
        "current_price": current_price,
        "total_value": current_price * quantity,
        "gain_loss": gain_loss,
        "purchase_date": datetime.strptime(purchase_date, '%Y-%m-%d'),  # Store as a datetime object
        "dividend_yield": dividend_yield,  # Store dividend yield
        "capital_gain_percentage": capital_gain_percentage,  # Store capital gain percentage
        "pe_ratio": pe_ratio,  # Store P/E Ratio
        "eps": eps,            # Store EPS
        "market_cap_category": market_cap_category  # Store Market Cap Category
    })

    save_portfolio(portfolio)  # Save updated portfolio after adding stock
    return redirect(url_for('index'))

@app.route('/remove_stock', methods=['POST'])
def remove_stock():
    symbol = request.form['symbol']
    
    # Find and remove stock from portfolio
    portfolio["stocks"] = [stock for stock in portfolio["stocks"] if stock["symbol"] != symbol]

    save_portfolio(portfolio)  # Save updated portfolio after removing stock
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
