import json
import os
from nicegui import ui

PORTFOLIO_FILE = "portfolio.json"

def load_portfolio():
    if not os.path.exists(PORTFOLIO_FILE):
        return []
    try:
        with open(PORTFOLIO_FILE, "r") as f:
            return json.load(f)
    except:
        return []

# --- NEW HELPER FOR HOME PAGE ---
def get_portfolio_tickers():
    """Returns a set of tickers currently in the portfolio for fast lookup."""
    data = load_portfolio()
    return {item['ticker'] for item in data}

def save_portfolio(data):
    with open(PORTFOLIO_FILE, "w") as f:
        json.dump(data, f, indent=4)

def add_transaction(ticker: str, qty: float, price: float):
    portfolio = load_portfolio()
    ticker = ticker.upper()
    
    try:
        qty = float(qty)
        price = float(price)
    except:
        ui.notify("Invalid Quantity or Price", color="red")
        return

    existing = next((item for item in portfolio if item["ticker"] == ticker), None)
    
    if existing:
        old_qty = float(existing.get("qty", 0))
        old_price = float(existing.get("avg_price", 0))
        new_total_qty = old_qty + qty
        
        if new_total_qty > 0:
            new_avg = ((old_qty * old_price) + (qty * price)) / new_total_qty
            existing["qty"] = new_total_qty
            existing["avg_price"] = new_avg
        else:
            portfolio.remove(existing)
    else:
        portfolio.append({
            "ticker": ticker,
            "qty": qty,
            "avg_price": price
        })
    
    save_portfolio(portfolio)

def remove_from_portfolio(ticker: str):
    portfolio = load_portfolio()
    portfolio = [p for p in portfolio if p["ticker"] != ticker]
    save_portfolio(portfolio)