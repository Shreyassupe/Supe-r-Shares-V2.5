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
# 1. DATA FETCHING (ROBUST & VERBOSE)
# ============================================================

@lru_cache(maxsize=128)
def fetch_yf(ticker: str, start: dt.date, end: dt.date) -> pd.DataFrame:
    try:
        # Suppress yfinance print noise
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            df = yf.download(
                ticker, 
                start=start, 
                end=end + dt.timedelta(days=1), 
                auto_adjust=False, 
                progress=False, 
                threads=True
            )
        
        if df.empty: 
            return pd.DataFrame()

        # Flatten MultiIndex columns if present (yfinance update fix)
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = [str(c[0]) for c in df.columns]
        
        df = df.reset_index()
        
        # Normalize column names
        colmap = {str(c).lower(): c for c in df.columns}
        date_col = colmap.get("date") or colmap.get("datetime") or colmap.get("index")
        
        if not date_col:
            return pd.DataFrame()

        df.rename(columns={date_col: "date"}, inplace=True)
        
        # Safe numeric conversion
        out = pd.DataFrame({
            "date": pd.to_datetime(df["date"]),
            "open": pd.to_numeric(df[colmap["open"]]),
            "high": pd.to_numeric(df[colmap["high"]]),
            "low": pd.to_numeric(df[colmap["low"]]),
            "close": pd.to_numeric(df.get(colmap.get("close"), df[colmap.get("adj close")])),
            "volume": pd.to_numeric(df[colmap["volume"]])
        })
        
        return out.dropna().sort_values("date").reset_index(drop=True)
    except Exception as e:
        print(f"Error fetching {ticker}: {e}")
        return pd.DataFrame()

@lru_cache(maxsize=64)
def fetch_fundamentals(ticker: str) -> dict:
    try: 
        return yf.Ticker(ticker).info
    except: 
        return {}

@lru_cache(maxsize=64)
def fetch_financials(ticker: str) -> pd.DataFrame:
    try:
        fin = yf.Ticker(ticker).financials
        return fin.T.sort_index() if not fin.empty else pd.DataFrame()
    except: 
        return pd.DataFrame()

@lru_cache(maxsize=64)
def fetch_holders(ticker: str) -> tuple:
    try:
        t = yf.Ticker(ticker)
        return t.major_holders, t.institutional_holders
    except: 
        return None, None

def fetch_news(query: str, limit: int = 5) -> list:
    news_results = []
    try:
        # Smart query switching for Market Indices
        if query in ["SPY", "^NSEI", "Market", "Stock Market"]:
            search_query = "Stock Market News" if query == "SPY" else "Indian Stock Market"
            try:
                search = yf.Search(search_query, news_count=limit)
                news_results = search.news
            except: pass

        if not news_results:
            t = yf.Ticker(query)
            news_results = t.news
            
        return news_results[:limit] if news_results else []
    except Exception as e:
        return []

# --- NEW: MARKET REGIME FETCHER ---
@lru_cache(maxsize=4)
def fetch_market_regime(market: str) -> dict:
    """
    Checks if the broader market (SPY or NIFTY) is in an uptrend.
    """
    ticker = "^NSEI" if market == "INDIA" else "SPY"
    end = dt.date.today()
    start = end - dt.timedelta(days=300)
    
    df = fetch_yf(ticker, start, end)
    
    if df.empty or len(df) < 200:
        return {"status": "NEUTRAL", "trend": "Unknown", "score_impact": 0, "ticker": ticker}
        
    df = add_indicators(df)
    last = df.iloc[-1]
    close = last["close"]
    ma50 = last["ma50"]
    ma200 = last["ma200"]
    
    if close > ma200:
        if close > ma50:
            return {"status": "BULL", "trend": "Strong Uptrend", "score_impact": 5, "ticker": ticker}
        else:
            return {"status": "CORRECTION", "trend": "Pullback in Bull Market", "score_impact": 0, "ticker": ticker}
    else:
        if close < ma50:
            return {"status": "BEAR", "trend": "Strong Downtrend", "score_impact": -15, "ticker": ticker}
        else:
            return {"status": "BEAR_RALLY", "trend": "Bear Market Rally", "score_impact": -5, "ticker": ticker}

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

    std20 = d["close"].rolling(20).std()
    d["bb_upper"] = d["ma20"] + (std20 * 2)
    d["bb_lower"] = d["ma20"] - (std20 * 2)

    exp12 = d["close"].ewm(span=12, adjust=False).mean()
    exp26 = d["close"].ewm(span=26, adjust=False).mean()
    d["macd"] = exp12 - exp26
    d["signal"] = d["macd"].ewm(span=9, adjust=False).mean()
    d["hist"] = d["macd"] - d["signal"]

    return d

# ============================================================
# 3. PATTERNS & HELPERS (FULL EXPANSION)
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
    if len(df) < 5: 
        return []
    
    tail = df.tail(n_days + 2).reset_index(drop=True)
    patterns = []
    
    for i in range(1, len(tail)):
        curr = tail.iloc[i]
        prev = tail.iloc[i-1]
        
        O = curr["open"]
        H = curr["high"]
        L = curr["low"]
        C = curr["close"]
        
        body = abs(C - O)
        rng = max(0.0001, H - L)
        upper_wick = H - max(O, C)
        lower_wick = min(O, C) - L
        
        pO = prev["open"]
        pC = prev["close"]
        pBody = abs(pC - pO)
        
        pBodyColor = "green" if pC > pO else "red"
        currBodyColor = "green" if C > O else "red"
        
        pat = None
        
        # Doji
        if body <= 0.15 * rng:
            pat = "Doji"
        # Hammer
        elif (lower_wick >= 2 * body) and (upper_wick <= 0.3 * body):
            pat = "Hammer"
        # Inverted Hammer / Shooting Star
        elif (upper_wick >= 2 * body) and (lower_wick <= 0.3 * body):
            if prev["close"] < prev["open"]:
                pat = "Inverted Hammer"
            else:
                pat = "Shooting Star"
        # Bullish Engulfing
        elif (body > pBody) and (C > pO and O < pC) and (currBodyColor == "green" and pBodyColor == "red"):
            pat = "Bullish Engulfing"
        # Bearish Engulfing
        elif (body > pBody) and (C < pO and O > pC) and (currBodyColor == "red" and pBodyColor == "green"):
            pat = "Bearish Engulfing"
        # Bearish Harami
        elif (body < pBody * 0.7) and (O > pC and C < pO) and (currBodyColor == "red" and pBodyColor == "green"):
            pat = "Bearish Harami"
        # Bullish Harami
        elif (body < pBody * 0.7) and (O < pC and C > pO) and (currBodyColor == "green" and pBodyColor == "red"):
            pat = "Bullish Harami"

        if pat:
            patterns.append({
                "Date": curr["date"], 
                "Pattern": pat, 
                "Meaning": CANDLE_LEARN.get(pat, ""), 
                "Learn": "https://www.investopedia.com/search?q=" + pat.replace(" ", "+")
            })
            
    return sorted(patterns, key=lambda x: x["Date"], reverse=True)[:n_days]

def explain_takeaways(df: pd.DataFrame):
    last = df.iloc[-1]
    ma20 = last.get("ma20")
    ma50 = last.get("ma50")
    ma200 = last.get("ma200")
    c = last["close"]
    
    short_term = f"Price is {'above' if c > ma20 else 'below'} MA20."
    medium_term = f"Trend is {'HEALTHY' if ma20 > ma50 else 'WEAK'}."
    long_term = f"Structure is {'POSITIVE' if ma50 > ma200 else 'NEGATIVE'}."
    
    return {
        "Short": short_term,
        "Medium": medium_term,
        "Long": long_term
    }

def get_pros_cons(df: pd.DataFrame) -> dict:
    # Legacy wrapper call
    dec = get_decision(df, profile="TRADER")
    return {"Pros": dec.get("Pros", []), "Cons": dec.get("Cons", [])}

def get_peers(ticker: str) -> list:
    me = next((c for c in COMPANIES if c["ticker"] == ticker), None)
    if not me: return []
    return [c for c in COMPANIES if c.get("sector") == me.get("sector") and c["ticker"] != ticker][:5]

# ============================================================
# 5. NEW: MULTI-FACTOR DECISION ENGINE (Quant V2)
# ============================================================

def get_decision(df: pd.DataFrame, profile: str = "TRADER", owned: bool = False, 
                 info: dict = None, roce_val: str = None, cagr_val: float = None, 
                 market_regime: dict = None) -> dict:
    
    # SAFE DEFAULT RETURN
    default_res = {
        "Decision": "WAIT", 
        "Archetype": "Analysis Pending", 
        "Score": 0, 
        "Reason": "Insufficient Data", 
        "Pros": [], 
        "Cons": [], 
        "Factors": {}, 
        "Stop": 0, 
        "Target": 0, 
        "ATR": 0, 
        "RSI": 50, 
        "Volatility": "Normal", 
        "Framework": profile,
        "Short": "Neutral",
        "Long": "Neutral",
        "Entry": "—"
    }

    if len(df) < 50: 
        return default_res

    # --- 1. SETUP PARAMETERS & WEIGHTS ---
    p = (profile or "TRADER").upper()
    is_investor = p == "INVESTOR"
    
    if is_investor:
        W = {"Quality": 0.40, "Value": 0.25, "Growth": 0.20, "Tech": 0.15}
    else: # TRADER
        W = {"Quality": 0.15, "Value": 0.15, "Growth": 0.10, "Tech": 0.60}

    last = df.iloc[-1]
    close = float(last["close"])
    atr = float(last.get("atr14", 0))
    rsi = float(last.get("rsi14", 50))
    ma20 = last.get("ma20", 0)
    ma50 = last.get("ma50", 0)
    ma200 = last.get("ma200", 0)
    
    pros = []
    cons = []

    # --- 2. DATA PREP & HARD VETO CHECKS ---
    roce_flt = 0.0
    if roce_val and "N/A" not in roce_val and "%" in roce_val:
        try: 
            roce_flt = float(roce_val.replace("%", "").strip())
        except: 
            pass
    
    cagr_flt = cagr_val if (cagr_val and cagr_val != "—") else 0.0
    
    roe = info.get("returnOnEquity", 0) if info else 0
    debt_eq = info.get("debtToEquity", 0) if info else 0
    peg = info.get("pegRatio", 0) if info else 0
    pe = info.get("trailingPE", 0) if info else 0
    
    # **HARD VETO 1: Capital Destruction**
    if is_investor and roce_flt < 0:
        return {
            "Decision": "AVOID", 
            "Archetype": "Capital Destroyer", 
            "Score": 10, 
            "Reason": f"**Hard Veto Triggered:** Negative ROCE ({roce_flt:.1f}%). Avoid.", 
            "Pros": [], 
            "Cons": ["Negative ROCE (Capital Destroyer)"], 
            "Factors": {"Quality": 0, "Value": 0, "Growth": 0, "Tech": 0, "Market": 50}, 
            "Stop": 0, 
            "Target": 0, 
            "ATR": atr, 
            "RSI": rsi, 
            "Volatility": "Normal", 
            "Framework": profile,
            "Short": "Bearish",
            "Long": "Bearish",
            "Entry": "—"
        }

    # --- 3. FACTOR SCORING (0-100) ---
    
    # A. QUALITY
    q_score = 50
    if roce_flt > 25: 
        q_score += 25
        pros.append(f"Elite ROCE ({roce_flt:.1f}%)")
    elif roce_flt > 15: 
        q_score += 15
        pros.append(f"Strong ROCE ({roce_flt:.1f}%)")
    elif roce_flt < 8: 
        q_score -= 15
        cons.append("Poor Capital Efficiency")
    
    if roe > 0.20: 
        q_score += 15
    
    if debt_eq > 200: 
        q_score -= 25
        cons.append("High Debt (>2x Equity)")
    
    q_final = max(0, min(100, q_score))

    # B. VALUE
    v_score = 50
    if 0 < peg < 1.0: 
        v_score += 30
        pros.append(f"Cheap for Growth (PEG {peg:.2f})")
    elif peg > 2.0: 
        v_score -= 20
        cons.append("Expensive Valuation")
    
    if 0 < pe < 15: 
        v_score += 20
        pros.append(f"Low P/E ({pe:.1f}x)")
    
    v_final = max(0, min(100, v_score))

    # C. GROWTH
    g_score = 50
    if cagr_flt > 20: 
        g_score += 30
        pros.append(f"High Speed Growth (+{cagr_flt:.1f}%)")
    elif cagr_flt > 12: 
        g_score += 15
    elif cagr_flt < 0: 
        g_score -= 25
        cons.append("Shrinking Business")
    
    g_final = max(0, min(100, g_score))

    # D. TECH
    t_score = 50
    if close > ma200:
        t_score += 10
        if ma50 > ma200: 
            t_score += 15
        if close > ma50: 
            t_score += 10
            pros.append("Strong Uptrend Structure")
    else:
        t_score -= 15
        if ma50 < ma200: 
            t_score -= 10
            cons.append("Long-term Downtrend")
        
    if 50 <= rsi <= 65: 
        t_score += 10
    elif rsi > 75: 
        t_score -= 5
        cons.append(f"Overbought (RSI {rsi:.0f})")
    elif rsi < 30: 
        t_score += 5
        pros.append("Oversold - Bounce likely")
    
    t_final = max(0, min(100, t_score))

    # E. MARKET
    m_impact = market_regime.get("score_impact", 0) if market_regime else 0
    m_status = market_regime.get("status", "NEUTRAL") if market_regime else "NEUTRAL"

    # --- 4. FINAL WEIGHTED SCORE ---
    base_score = (q_final * W["Quality"]) + (v_final * W["Value"]) + (g_final * W["Growth"]) + (t_final * W["Tech"])
    final_score = base_score + m_impact
    final_score = int(max(0, min(100, final_score)))

    # --- 5. DETAILED NARRATIVE GENERATION (The "Why") ---
    bullets = []
    
    # Quality Bullet (With Values)
    if q_final > 70: 
        bullets.append(f"**Robust Fundamentals:** High capital efficiency with **ROCE of {roce_flt:.1f}%** and **ROE of {roe*100:.1f}%** indicates a strong moat.")
    elif q_final < 40: 
        bullets.append(f"**Weak Fundamentals:** Low efficiency (**ROCE {roce_flt:.1f}%**) suggests capital allocation issues.")
    else: 
        bullets.append(f"**Stable Fundamentals:** Moderate efficiency with **ROCE of {roce_flt:.1f}%**. Business is stable but not elite.")

    # Value Bullet (With Values)
    if v_final > 70: 
        bullets.append(f"**Attractive Valuation:** Stock is undervalued relative to growth. **PEG Ratio is {peg:.2f}**, which is excellent.")
    elif v_final < 40: 
        bullets.append(f"**Premium Valuation:** Priced for perfection. **P/E is {pe:.1f}** and **PEG is {peg:.2f}**, indicating expensive pricing.")
    else: 
        bullets.append(f"**Fair Valuation:** Priced in line with earnings (**P/E {pe:.1f}**). Neither cheap nor expensive.")

    # Growth Bullet (With Values)
    if g_final > 70: 
        bullets.append(f"**High Growth Engine:** Strong 3-Year performance of **{cagr_flt:.1f}% CAGR** confirms momentum.")
    elif g_final < 40: 
        bullets.append(f"**Slowing Growth:** 3-Year CAGR is low or negative (**{cagr_flt:.1f}%**).")
    
    # Tech Bullet (With Values)
    if t_final > 70: 
        bullets.append(f"**Bullish Trend:** Price is above the 200-day Moving Average. **RSI is {rsi:.0f}**, indicating healthy momentum.")
    elif t_final < 40: 
        bullets.append(f"**Bearish Trend:** Price is below key averages. Technical structure is weak.")

    if m_status == "BEAR": 
        bullets.append("**Market Headwind:** The broader market (NIFTY/SPY) is in a downtrend, increasing risk for individual longs.")

    full_reason = "\n\n".join([f"- {b}" for b in bullets])

    # --- 6. ARCHETYPE CLASSIFICATION ---
    archetype = "General Analysis"
    decision = "WAIT"
    
    if close < ma200 and ma50 < ma200:
        archetype = "Falling Knife" if rsi < 35 else "Broken Trend"
        decision = "AVOID"
    elif q_final > 80 and g_final > 70:
        archetype = "Quality Compounder"
        decision = "BUY" if final_score > 75 else "ACCUMULATE"
    elif t_final > 85 and g_final > 60 and v_final < 40:
        archetype = "Momentum Rocket"
        decision = "BUY" if final_score > 80 else "WAIT"
    elif v_final > 80 and q_final < 50:
        archetype = "Value Trap Risk"
        decision = "AVOID"
    else:
        if final_score >= 85: 
            archetype = "Strong Buy"
            decision = "BUY"
        elif final_score >= 70: 
            archetype = "Accumulate"
            decision = "BUY"
        elif final_score <= 40: 
            archetype = "Underperformer"
            decision = "AVOID"
        else: 
            archetype = "Neutral"
            decision = "WAIT"

    # Stops & Volatility
    vol_atr_mult = 2.5 if is_investor else 1.5
    stop_price = close - (vol_atr_mult * atr)
    target_price = close + (vol_atr_mult * 2.5 * atr)
    vol_type = "High" if last["atr_pct"] > 3 else "Normal"

    # --- 7. DYNAMIC FRAMEWORK & TRENDS ---
    framework = "INVEST" if final_score > 60 else profile 
    short_trend = "Bullish" if close > ma20 else "Bearish"
    long_trend = "Bullish" if close > ma200 else "Bearish"

    # SMART ENTRY LOGIC
    if decision == "BUY":
        entry_signal = f"Buy @ {ma20:.2f}"
    elif close < ma20:
        entry_signal = f"Reclaim > {ma20:.2f}"
    else:
        entry_signal = f"Support {ma20:.2f}"

    # --- 8. CONTEXTUAL OVERRIDE (THE FIX) ---
    # Fix for UPS scenario: High Tech Score (Trend) but Low Growth (CAGR)
    # If Decision is BUY but Growth is < 5%, downgrade to SWING.
    if ("BUY" in decision or "INVEST" in decision) and cagr_flt < 5.0:
        decision = "SWING"
        archetype = "Swing Trade"
        # Optional: Cap score to reflect it's not a perfect buy
        if final_score > 75: final_score = 75 
    
    # If Decision is WAIT but Growth is High (> 20%), upgrade to WATCH (Dip Buy candidate)
    elif ("WAIT" in decision or "AVOID" in decision) and cagr_flt > 20.0:
        decision = "WATCH"
        archetype = "High Growth Watch"

    return {
        "Decision": decision,
        "Archetype": archetype,
        "Score": final_score,
        "Reason": full_reason,
        "Pros": pros[:4],
        "Cons": cons[:4],
        "Factors": {
            "Quality": int(q_final), 
            "Value": int(v_final), 
            "Growth": int(g_final), 
            "Tech": int(t_final), 
            "Market": int(50 + m_impact)
        },
        "Stop": stop_price,
        "Target": target_price,
        "ATR": atr, 
        "RSI": rsi,
        "Volatility": vol_type,
        "Framework": framework,
        "Short": short_trend,
        "Long": long_trend,
        "Entry": entry_signal
    }

# ============================================================
# 6. BACKTESTING & SCORING (RESTORED FULL LOOPS)
# ============================================================

def backtest_stock(df: pd.DataFrame, profile: str = "TRADER") -> dict:
    if len(df) < 200: 
        return {}
    
    capital = 10000
    shares = 0
    in_trade = False
    stop_price = 0.0
    target_price = 0.0
    trades = []
    
    for i in range(200, len(df)):
        window = df.iloc[:i+1]
        today = df.iloc[i]
        price = today["close"]
        date = today["date"]
        
        if in_trade:
            if price <= stop_price:
                # Stop Loss
                rev = shares * price
                trades.append({
                    "Date": date, 
                    "Type": "SELL", 
                    "Price": price, 
                    "Reason": "Stop Loss", 
                    "Profit": rev - capital
                })
                capital = rev
                in_trade = False
            elif price >= target_price:
                # Target Hit
                rev = shares * price
                trades.append({
                    "Date": date, 
                    "Type": "SELL", 
                    "Price": price, 
                    "Reason": "Target Hit", 
                    "Profit": rev - capital
                })
                capital = rev
                in_trade = False
        else:
            # Buy Logic
            sig = get_decision(window, profile, owned=False)
            if sig["Decision"] == "BUY":
                stop_price = sig["Stop"]
                target_price = sig["Target"]
                shares = capital / price
                trades.append({
                    "Date": date, 
                    "Type": "BUY", 
                    "Price": price, 
                    "Stop": stop_price, 
                    "Target": target_price
                })
                in_trade = True

    wins = len([t for t in trades if t["Type"] == "SELL" and t["Profit"] > 0])
    total = len([t for t in trades if t["Type"] == "SELL"])
    
    return {
        "Initial Capital": 10000,
        "Final Capital": capital,
        "Return %": ((capital-10000)/10000)*100,
        "Total Trades": total,
        "Win Rate": (wins/total*100) if total else 0,
        "Trade Log": trades
    }

def score_universe_data(companies: list, lookback_days: int = 120, profile: str = "TRADER") -> pd.DataFrame:
    end = dt.date.today()
    start = end - dt.timedelta(days=lookback_days + 260)
    rows = []
    
    for c in companies:
        df = fetch_yf(c["ticker"], start, end)
        if len(df) < 60: 
            continue
        
        df = add_indicators(df)
        
        # Simple decision call for Home Page (Lightweight)
        sig = get_decision(df, profile, owned=False)
        
        last = df.iloc[-1]
        prev = df.iloc[-2]
        chg = last["close"] - prev["close"]
        dist_ma20 = ((last["close"] - last["ma20"]) / last["ma20"]) * 100
        
        rows.append({
            "Ticker": c["ticker"],
            "Company": c["name"],
            "Sector": c.get("sector", "Other"),
            "Decision": sig["Decision"],
            "Reason": sig["Reason"],
            "Conf": sig.get("Conf", "Medium"), # Fallback
            "Entry": sig.get("Entry", ""),
            "Stop": sig["Stop"],
            "Target": sig["Target"],
            "Framework": sig["Framework"],
            "Score": sig["Score"],
            "Short": sig.get("Short", "Neutral"),
            "Long": sig.get("Long", "Neutral"),
            "Volatility": sig["Volatility"],
            "Last Close": last["close"],
            "Change": chg,
            "Change%": (chg/prev["close"])*100,
            "Volume": last["volume"],
            "ATR": sig["ATR"],
            "RSI": sig["RSI"],
            "DistMA20": dist_ma20
        })
    
    return pd.DataFrame(rows)

def score_portfolio(portfolio_items: list, profile: str = "TRADER") -> pd.DataFrame:
    end = dt.date.today()
    start = end - dt.timedelta(days=365)
    rows = []
    
    for item in portfolio_items:
        t = item["ticker"]; qty = float(item["qty"]); avg = float(item["avg_price"])
        comp = next((c for c in COMPANIES if c["ticker"] == t), {"name": t})
        df = fetch_yf(t, start, end)
        if len(df) >= 60:
            df = add_indicators(df)
            sig = get_decision(df, profile, owned=True)
            curr = float(df.iloc[-1]["close"])
            rows.append({
                "Ticker": t,
                "Company": comp.get("name", t),
                "Sector": comp.get("sector", "Other"),
                "Qty": qty,
                "AvgPrice": avg,
                "CurrentPrice": curr,
                "Invested": qty*avg,
                "CurrentVal": qty*curr,
                "P&L": (qty*curr)-(qty*avg),
                "P&L%": (((qty*curr)-(qty*avg))/(qty*avg)*100) if avg else 0,
                "DailyP&L": (curr - df.iloc[-2]["close"]) * qty,
                "DailyChg%": ((curr - df.iloc[-2]["close"])/df.iloc[-2]["close"])*100,
                "Decision": sig["Decision"],
                "Reason": sig["Reason"],
                "Framework": sig["Framework"]
            })
    return pd.DataFrame(rows)

# ============================================================
# 7. FAVORITES UTILS
# ============================================================
def get_favorites(): 
    return app.storage.user.get("favorites", [])

def toggle_favorite(ticker: str):
    favs = list(app.storage.user.get("favorites", []))
    if ticker in favs: 
        favs.remove(ticker)
    else: 
        favs.append(ticker)
    app.storage.user["favorites"] = favs

def is_favorite(ticker: str) -> bool: 
    return ticker in get_favorites()