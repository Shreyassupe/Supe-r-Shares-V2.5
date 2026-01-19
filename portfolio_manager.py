import json
import os
import datetime as dt
import yfinance as yf

DATA_FILE = "portfolio.json"

# ============================================================
# 1. CORE DATA MANAGEMENT
# ============================================================

def load_data_structure():
    """
    Loads data and handles MIGRATION from old List format to new Dict format.
    New Format: { "holdings": [...], "history": [...] }
    """
    if not os.path.exists(DATA_FILE):
        return {"holdings": [], "history": []}
    
    try:
        with open(DATA_FILE, "r") as f:
            data = json.load(f)
            
        # MIGRATION: If old format (List), convert to New Format (Dict)
        if isinstance(data, list):
            new_structure = {"holdings": [], "history": []}
            for item in data:
                # If Qty > 0, it's a holding
                if float(item.get("qty", 0)) > 0:
                    new_structure["holdings"].append(item)
                
                # If it has realized gain, save it as a legacy history record
                r_gain = float(item.get("realized_gain", 0))
                if r_gain != 0:
                    # Legacy records won't have exact sell prices, so we infer or mark them
                    new_structure["history"].append({
                        "ticker": item["ticker"],
                        "buy_price": item.get("avg_price", 0),
                        "sell_price": 0, # Legacy: Unknown
                        "qty_sold": 0,   # Legacy: Unknown
                        "profit": r_gain,
                        "date": dt.date.today().strftime("%Y-%m-%d"),
                        "notes": "Imported History"
                    })
            
            # Save the new structure immediately
            save_data_structure(new_structure)
            return new_structure
            
        return data
    except:
        return {"holdings": [], "history": []}

def save_data_structure(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

# ============================================================
# 2. GETTERS
# ============================================================

def get_active_holdings():
    """Returns only currently owned stocks."""
    data = load_data_structure()
    return data.get("holdings", [])

def get_trade_history():
    """Returns the log of all closed positions (sales)."""
    data = load_data_structure()
    return data.get("history", [])

# ============================================================
# 3. ACTIONS
# ============================================================

def add_transaction(ticker, qty, price):
    data = load_data_structure()
    holdings = data["holdings"]
    
    # Check if we already own this stock
    existing = next((item for item in holdings if item["ticker"] == ticker), None)
    
    qty = float(qty)
    price = float(price)
    
    if existing:
        # Average Down/Up Logic
        old_qty = float(existing["qty"])
        old_price = float(existing["avg_price"])
        total_shares = old_qty + qty
        
        if total_shares > 0:
            existing["avg_price"] = ((old_qty * old_price) + (qty * price)) / total_shares
        else:
            existing["avg_price"] = price
        existing["qty"] = total_shares
    else:
        # New Position
        holdings.append({
            "ticker": ticker, 
            "qty": qty, 
            "avg_price": price, 
            "realized_gain": 0.0 # Kept for backward compatibility
        })
    
    save_data_structure(data)

def sell_stock(ticker, qty_to_sell, sell_price):
    data = load_data_structure()
    holdings = data["holdings"]
    history = data["history"]
    
    existing = next((item for item in holdings if item["ticker"] == ticker), None)
    
    if existing:
        current_qty = float(existing["qty"])
        qty_to_sell = float(qty_to_sell)
        sell_price = float(sell_price)
        
        if qty_to_sell > current_qty: return False
        
        # 1. Calculate Profit for this specific sale
        avg_cost = float(existing["avg_price"])
        profit = (sell_price - avg_cost) * qty_to_sell
        
        # 2. Add to HISTORY Log (This is the new feature!)
        history.append({
            "ticker": ticker,
            "buy_price": avg_cost,
            "sell_price": sell_price,
            "qty_sold": qty_to_sell,
            "profit": profit,
            "date": dt.date.today().strftime("%Y-%m-%d")
        })
        
        # 3. Update Holdings
        new_qty = current_qty - qty_to_sell
        
        if new_qty <= 0:
            # Fully Sold - Remove from holdings list completely
            # (It still exists in history list, so we don't lose the record)
            holdings.remove(existing)
        else:
            # Partial Sell - Just reduce quantity
            existing["qty"] = new_qty
        
        save_data_structure(data)
        return True
    return False

def remove_from_portfolio(ticker):
    """Deletes a stock from holdings (Undo Buy). Does not touch history."""
    data = load_data_structure()
    data["holdings"] = [d for d in data["holdings"] if d["ticker"] != ticker]
    save_data_structure(data)

# Compatibility wrapper for Home Page
def get_portfolio_tickers():
    return [d["ticker"] for d in get_active_holdings()]