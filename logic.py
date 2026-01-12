import datetime as dt
import numpy as np
import pandas as pd
import yfinance as yf
from functools import lru_cache
from nicegui import app
from universe import COMPANIES
import contextlib
import io

# ============================================================
# 1. DATA FETCHING
# ============================================================

@lru_cache(maxsize=128)
def fetch_yf(ticker: str, start: dt.date, end: dt.date) -> pd.DataFrame:
    try:
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            df = yf.download(
                ticker, 
                start=start, 
                end=end + dt.timedelta(days=1), 
                auto_adjust=False, 
                progress=False, 
                threads=True
            )
        
        if df.empty: return pd.DataFrame()
        
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = [str(c[0]) for c in df.columns]
        
        df = df.reset_index()
        colmap = {str(c).lower(): c for c in df.columns}
        date_col = colmap.get("date") or colmap.get("datetime") or colmap.get("index")
        df.rename(columns={date_col: "date"}, inplace=True)
        
        out = pd.DataFrame({
            "date": pd.to_datetime(df["date"]),
            "open": pd.to_numeric(df[colmap["open"]]),
            "high": pd.to_numeric(df[colmap["high"]]),
            "low": pd.to_numeric(df[colmap["low"]]),
            "close": pd.to_numeric(df.get(colmap.get("close"), df[colmap.get("adj close")])),
            "volume": pd.to_numeric(df[colmap["volume"]])
        })
        return out.dropna().sort_values("date").reset_index(drop=True)
    except:
        return pd.DataFrame()

# --- Deep Data Fetchers ---
@lru_cache(maxsize=64)
def fetch_fundamentals(ticker: str) -> dict:
    try:
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            return yf.Ticker(ticker).info
    except: return {}

@lru_cache(maxsize=64)
def fetch_financials(ticker: str) -> pd.DataFrame:
    try:
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            fin = yf.Ticker(ticker).financials
            return fin.T.sort_index() if not fin.empty else pd.DataFrame()
    except: return pd.DataFrame()

@lru_cache(maxsize=64)
def fetch_holders(ticker: str) -> tuple:
    try:
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            t = yf.Ticker(ticker)
            return t.major_holders, t.institutional_holders
    except: return None, None

# ============================================================
# 2. TECHNICAL INDICATORS
# ============================================================

def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    d = df.copy()
    d["ma20"] = d["close"].rolling(20).mean()
    d["ma50"] = d["close"].rolling(50).mean()
    d["ma200"] = d["close"].rolling(200).mean()
    
    delta = d["close"].diff()
    gain = delta.where(delta > 0, 0.0).ewm(alpha=1/14, adjust=False).mean()
    loss = (-delta).where(delta < 0, 0.0).ewm(alpha=1/14, adjust=False).mean()
    rs = gain / loss.replace(0, np.nan)
    d["rsi14"] = 100 - (100 / (1 + rs))
    
    pc = d["close"].shift(1)
    tr = pd.concat([(d["high"]-d["low"]).abs(), (d["high"]-pc).abs(), (d["low"]-pc).abs()], axis=1).max(axis=1)
    d["atr14"] = tr.ewm(alpha=1/14, adjust=False).mean()
    d["atr_pct"] = (d["atr14"] / d["close"]) * 100
    return d

# ============================================================
# 3. CANDLE PATTERNS
# ============================================================

CANDLE_LEARN = {
    "Doji": "Indecision: open ≈ close.",
    "Hammer": "Possible bullish reversal found at bottoms.",
    "Inverted Hammer": "Possible bullish reversal attempt.",
    "Shooting Star": "Bearish reversal signal found at tops.",
    "Bullish Engulfing": "Strong bullish move swallowing previous red candle.",
    "Bearish Engulfing": "Strong bearish move swallowing previous green candle.",
    "Bullish Harami": "Downtrend pausing (small green inside large red).",
    "Bearish Harami": "Uptrend pausing (small red inside large green)."
}

def detect_patterns(df: pd.DataFrame, n_days: int = 5):
    if len(df) < 5: return []
    tail = df.tail(n_days + 2).reset_index(drop=True)
    patterns = []
    
    for i in range(1, len(tail)):
        curr = tail.iloc[i]
        prev = tail.iloc[i-1]
        O, H, L, C = curr["open"], curr["high"], curr["low"], curr["close"]
        body = abs(C - O)
        rng = max(0.0001, H - L)
        upper_wick = H - max(O, C)
        lower_wick = min(O, C) - L
        
        pO, pC = prev["open"], prev["close"]
        pBody = abs(pC - pO)
        pBodyColor = "green" if pC > pO else "red"
        currBodyColor = "green" if C > O else "red"
        
        pat = None
        if body <= 0.15 * rng: pat = "Doji"
        elif (lower_wick >= 2 * body) and (upper_wick <= 0.3 * body): pat = "Hammer"
        elif (upper_wick >= 2 * body) and (lower_wick <= 0.3 * body): pat = "Inverted Hammer" if prev["close"] < prev["open"] else "Shooting Star"
        elif (body > pBody) and (C > pO and O < pC) and (currBodyColor == "green" and pBodyColor == "red"): pat = "Bullish Engulfing"
        elif (body > pBody) and (C < pO and O > pC) and (currBodyColor == "red" and pBodyColor == "green"): pat = "Bearish Engulfing"
        elif (body < pBody * 0.7) and (O > pC and C < pO) and (currBodyColor == "red" and pBodyColor == "green"): pat = "Bearish Harami"
        elif (body < pBody * 0.7) and (O < pC and C > pO) and (currBodyColor == "green" and pBodyColor == "red"): pat = "Bullish Harami"

        if pat:
            patterns.append({
                "Date": curr["date"], "Pattern": pat, 
                "Meaning": CANDLE_LEARN.get(pat, ""), 
                "Learn": "https://www.investopedia.com/search?q=" + pat.replace(" ", "+")
            })
            
    return sorted(patterns, key=lambda x: x["Date"], reverse=True)[:n_days]

# ============================================================
# 4. TEXT ANALYSIS
# ============================================================

def explain_takeaways(df: pd.DataFrame):
    last = df.iloc[-1]
    ma20, ma50, ma200 = last.get("ma20"), last.get("ma50"), last.get("ma200")
    c = last["close"]
    return {
        "Short": f"Price is {'above' if c > ma20 else 'below'} MA20.",
        "Medium": f"Trend is {'HEALTHY' if ma20 > ma50 else 'WEAK'}.",
        "Long": f"Structure is {'POSITIVE' if ma50 > ma200 else 'NEGATIVE'}."
    }

def get_pros_cons(df: pd.DataFrame) -> dict:
    last = df.iloc[-1]
    pros, cons = [], []
    if last["close"] > last["ma200"]: pros.append("Trading above 200-day MA (Bullish).")
    else: cons.append("Trading below 200-day MA (Bearish).")
    if last["rsi14"] < 35: pros.append("RSI is Oversold (Potential bounce).")
    elif last["rsi14"] > 65: cons.append("RSI is Overbought (Caution).")
    if last["atr_pct"] < 1.5: pros.append("Volatility is Low (Stable).")
    return {"Pros": pros, "Cons": cons}

def get_peers(ticker: str) -> list:
    me = next((c for c in COMPANIES if c["ticker"] == ticker), None)
    if not me: return []
    return [c for c in COMPANIES if c.get("sector") == me.get("sector") and c["ticker"] != ticker][:5]

# ============================================================
# 5. DECISION ENGINE
# ============================================================

def get_decision(df: pd.DataFrame, profile: str = "TRADER", owned: bool = False) -> dict:
    p = (profile or "TRADER").upper()
    if p == "SWING":
        par = {"stop_atr": 2.5, "target_r": 2.5, "rsi_min": 35}
    else:
        par = {"stop_atr": 2.0, "target_r": 2.0, "rsi_min": 40}
    
    last = df.iloc[-1]
    close = float(last["close"])
    atr = float(last.get("atr14", 0))
    rsi = float(last.get("rsi14", 50))
    
    med = "Bullish" if last["ma20"] > last["ma50"] else "Bearish"
    lng = "Uptrend" if last["ma50"] > last["ma200"] else "Downtrend"
    vol = "High" if last["atr_pct"] > 2.5 else ("Low" if last["atr_pct"] < 1.2 else "Normal")
    short = "Bullish candle" if close > last["open"] else "Bearish candle"
    
    fw = "INVEST" if lng == "Uptrend" and med == "Bullish" and vol != "High" else ("AVOID" if lng == "Downtrend" else "WAIT")
    decision, entry = "WAIT", ""
    
    dist = atr * 1.2
    near_ma = abs(close - last["ma20"]) < dist or abs(close - last["ma50"]) < dist
    
    if fw == "INVEST" and near_ma and par["rsi_min"] <= rsi <= 60:
        decision, entry = "BUY", "Pullback to MA"
    elif fw == "AVOID":
        decision = "AVOID"
    
    # --- V2.0 FEATURE: OWNERSHIP LOGIC ---
    # If we own the stock, and the framework says AVOID (Downtrend), warn the user to SELL.
    if owned and fw == "AVOID":
        decision = "SELL WARNING"

    stop = close - (par["stop_atr"] * atr) if decision == "BUY" else np.nan
    target = close + (par["target_r"] * (close - stop)) if decision == "BUY" else np.nan
    
    base_score = 45 if fw == "INVEST" else 25
    if decision == "BUY": base_score += 10
    if decision == "SELL WARNING": base_score = 10 # Penalize score heavily for sell warnings
    
    return {
        "Decision": decision, "Conf": "High" if decision in ["BUY", "SELL WARNING"] else "Medium", 
        "Entry": entry, "Stop": stop, "Target": target, 
        "Framework": fw, "Score": base_score, 
        "Short": short, "Medium": med, "Long": lng, 
        "Volatility": vol, "ATR": atr, "RSI": rsi
    }

# ============================================================
# 6. SCORING LOOPS (UNIVERSE & PORTFOLIO)
# ============================================================

def score_universe_data(companies: list, lookback_days: int = 120, profile: str = "TRADER") -> pd.DataFrame:
    end = dt.date.today()
    start = end - dt.timedelta(days=lookback_days + 260)
    rows = []
    
    for c in companies:
        df = fetch_yf(c["ticker"], start, end)
        if len(df) < 60: continue
        df = add_indicators(df)
        sig = get_decision(df, profile, owned=False)
        last, prev = df.iloc[-1], df.iloc[-2]
        chg = last["close"] - prev["close"]
        chg_pct = (chg / prev["close"]) * 100
        dist_ma20 = ((last["close"] - last["ma20"]) / last["ma20"]) * 100
        
        rows.append({
            "Ticker": c["ticker"], "Company": c["name"], "Sector": c.get("sector", "Other"),
            "Decision": sig["Decision"], "Conf": sig["Conf"], "Entry": sig["Entry"],
            "Stop": sig["Stop"], "Target": sig["Target"], "Framework": sig["Framework"],
            "Score": sig["Score"], "Short": sig["Short"], "Medium": sig["Medium"], "Long": sig["Long"],
            "Volatility": sig["Volatility"], "Last Close": last["close"], 
            "Change": chg, "Change%": chg_pct, "Volume": last["volume"],
            "ATR": sig["ATR"], "RSI": sig["RSI"], "DistMA20": dist_ma20
        })
    return pd.DataFrame(rows)

def score_portfolio(portfolio_items: list, profile: str = "TRADER") -> pd.DataFrame:
    """
    V2.0 New Function: Scores only the items in the portfolio and adds P&L math.
    """
    end = dt.date.today()
    start = end - dt.timedelta(days=365) # 1 year lookback for owners
    rows = []
    
    for item in portfolio_items:
        ticker = item["ticker"]
        qty = float(item["qty"])
        avg_price = float(item["avg_price"])
        
        # Find company name if possible
        comp = next((c for c in COMPANIES if c["ticker"] == ticker), {"name": ticker})
        
        df = fetch_yf(ticker, start, end)
        if len(df) < 60: continue
        df = add_indicators(df)
        
        # PASS owned=True to trigger SELL WARNING logic
        sig = get_decision(df, profile, owned=True)
        
        last = df.iloc[-1]
        current_price = float(last["close"])
        
        # --- WALLET MATH ---
        invested_amt = qty * avg_price
        current_val = qty * current_price
        pl = current_val - invested_amt
        pl_pct = (pl / invested_amt * 100) if invested_amt > 0 else 0
        
        rows.append({
            "Ticker": ticker,
            "Company": comp["name"],
            "Qty": qty,
            "AvgPrice": avg_price,
            "CurrentPrice": current_price,
            "Invested": invested_amt,
            "CurrentVal": current_val,
            "P&L": pl,
            "P&L%": pl_pct,
            "Decision": sig["Decision"], # This will now show "SELL WARNING" if needed
            "Score": sig["Score"],
            "Framework": sig["Framework"]
        })
        
    return pd.DataFrame(rows)

# ============================================================
# 7. FAVORITES UTILS
# ============================================================
def get_favorites(): return app.storage.user.get("favorites", [])

def toggle_favorite(ticker: str):
    favs = list(app.storage.user.get("favorites", []))
    if ticker in favs: favs.remove(ticker)
    else: favs.append(ticker)
    app.storage.user["favorites"] = favs

def is_favorite(ticker: str) -> bool: return ticker in get_favorites()