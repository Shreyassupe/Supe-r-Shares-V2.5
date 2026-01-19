import datetime as dt
import numpy as np
import pandas as pd
import yfinance as yf
import contextlib
import io

# ============================================================
# 1. RISK ENGINE (CORRELATION MATRIX)
# ============================================================
def get_portfolio_correlation(tickers: list) -> dict:
    """
    Calculates Pearson Correlation Matrix and a Diversity Score.
    """
    if len(tickers) < 2:
        return {"matrix": pd.DataFrame(), "diversity_score": 0, "msg": "Need 2+ stocks"}

    try:
        # Bulk Fetch Last 1 Year
        end = dt.date.today()
        start = end - dt.timedelta(days=365)
        
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            # Fetch Close prices
            data = yf.download(tickers, start=start, end=end, progress=False)['Close']
        
        if data.empty: return {"matrix": pd.DataFrame(), "diversity_score": 0}

        # Calculate Returns
        returns = data.pct_change().dropna()

        # Correlation Matrix
        corr_matrix = returns.corr()

        # Diversity Score Algorithm
        mask = np.tril(np.ones(corr_matrix.shape), k=-1).astype(bool)
        correlations = corr_matrix.where(mask).stack().values
        
        if len(correlations) > 0:
            avg_corr = np.mean(correlations)
            diversity_score = max(0, min(100, 100 - (avg_corr * 100)))
        else:
            diversity_score = 0

        return {
            "matrix": corr_matrix,
            "diversity_score": int(diversity_score),
            "msg": "Success"
        }

    except Exception as e:
        print(f"Risk Engine Error: {e}")
        return {"matrix": pd.DataFrame(), "diversity_score": 0, "msg": str(e)}

# ============================================================
# 2. QUANT DNA ENGINE (FACTOR ANALYSIS)
# ============================================================
def get_quant_dna(ticker: str, info: dict, df: pd.DataFrame) -> dict:
    """
    Calculates 0-100 scores for Value, Momentum, Quality, and Stability.
    """
    if df.empty: return {}

    # A. VALUE (P/E Ratio)
    pe = info.get("trailingPE", 50)
    if pe is None: pe = 50
    value_score = max(0, min(100, 100 - (pe * 1.5))) 
    
    # B. MOMENTUM (RSI + Trend)
    last = df.iloc[-1]
    rsi = last.get("rsi14", 50)
    mom_score = rsi 
    if last["close"] > last["ma50"]: mom_score += 10
    mom_score = max(0, min(100, mom_score))

    # C. QUALITY (Margins + ROE)
    margins = info.get("profitMargins", 0) or 0
    roe = info.get("returnOnEquity", 0) or 0
    quality_score = max(0, min(100, (margins * 100 * 2.5) + (roe * 100 * 1.5)))

    # D. STABILITY (Beta)
    beta = info.get("beta", 1.0)
    if beta is None: beta = 1.0
    stability_score = max(0, min(100, 120 - (beta * 50)))

    return {
        "Value": int(value_score),
        "Momentum": int(mom_score),
        "Quality": int(quality_score),
        "Stability": int(stability_score)
    }

# ============================================================
# 3. MONTE CARLO SIMULATOR
# ============================================================
def run_monte_carlo(df: pd.DataFrame, days: int = 30, simulations: int = 1000) -> dict:
    if len(df) < 100: return {}

    try:
        returns = df["close"].pct_change().dropna()
        u = returns.mean()
        var = returns.var()
        drift = u - (0.5 * var)
        sigma = returns.std()
        
        last_price = df.iloc[-1]["close"]
        daily_returns = np.exp(drift + sigma * np.random.normal(0, 1, (days, simulations)))
        
        price_paths = np.zeros((days, simulations))
        price_paths[0] = last_price
        
        for t in range(1, days):
            price_paths[t] = price_paths[t-1] * daily_returns[t]

        results = {
            "p95": np.percentile(price_paths, 95, axis=1),
            "p50": np.percentile(price_paths, 50, axis=1),
            "p05": np.percentile(price_paths, 5, axis=1),
            "start_price": last_price,
            "end_date": df.iloc[-1]["date"] + dt.timedelta(days=days)
        }
        return results

    except Exception as e:
        print(f"Monte Carlo Error: {e}")
        return {}

# ============================================================
# 4. FUNDAMENTAL METRICS (ROCE & PERFORMANCE)
# ============================================================

def calculate_roce(ticker: str) -> dict:
    """
    Robust ROCE Calculator.
    Formula: EBIT / (Total Assets - Current Liabilities)
    """
    try:
        t = yf.Ticker(ticker)
        fin = t.financials
        bs = t.balance_sheet
        
        if fin.empty or bs.empty:
            return {"current": "N/A", "avg3y": "N/A"}

        # Helper to find row case-insensitively
        def get_row(df, keys):
            # Normalize index to lower case stripped
            df.index = df.index.str.lower().str.strip()
            for k in keys:
                k_norm = k.lower().strip()
                if k_norm in df.index:
                    return df.loc[k_norm]
            return None

        # Try multiple aliases for keys
        ebit_row = get_row(fin, ["EBIT", "Ebit", "Operating Income", "Net Income Continuous Operations"])
        assets_row = get_row(bs, ["Total Assets", "Assets"])
        liab_row = get_row(bs, ["Total Current Liabilities", "Current Liabilities", "Total Liabilities Net Minority Interest"])

        if ebit_row is None or assets_row is None:
            return {"current": "N/A", "avg3y": "N/A"}

        roces = []
        # Calculate for last 4 available years
        for date in fin.columns[:4]: 
            try:
                ebit = ebit_row[date]
                assets = assets_row[date]
                
                # If current liabilities missing, approximate Capital Employed as Total Equity + Non-Current Liab
                # Or just use Total Assets if Liab missing (rough estimate)
                liab = liab_row[date] if liab_row is not None else 0
                
                capital_employed = assets - liab
                
                if capital_employed > 0:
                    roce = (ebit / capital_employed) * 100
                    roces.append(roce)
            except: pass
            
        if not roces: return {"current": "N/A", "avg3y": "N/A"}

        current_roce = roces[0]
        avg_roce = sum(roces[:3]) / len(roces[:3]) if len(roces) >= 3 else sum(roces) / len(roces)

        return {
            "current": f"{current_roce:.2f}%",
            "avg3y": f"{avg_roce:.2f}%"
        }
    except Exception as e:
        print(f"ROCE Calculation Error for {ticker}: {e}")
        return {"current": "N/A", "avg3y": "N/A"}

def get_performance_stats(df: pd.DataFrame) -> dict:
    """
    Calculates % gain/loss for 1W, 1M, 1Y, 3Y, 5Y based on historical data.
    """
    if df.empty: return {}
    
    df = df.sort_values("date").reset_index(drop=True)
    current_price = df.iloc[-1]["close"]
    last_date = df.iloc[-1]["date"]
    
    def get_change(days_back):
        target_date = last_date - dt.timedelta(days=days_back)
        past_rows = df[df["date"] <= target_date]
        if past_rows.empty: return "—"
        
        # Get the row closest to the target date (tail(1) is closest since we filtered <=)
        past_price = past_rows.iloc[-1]["close"]
        if past_price == 0: return "—"
        
        pct = ((current_price - past_price) / past_price) * 100
        return pct

    return {
        "1W": get_change(7),
        "1M": get_change(30),
        "1Y": get_change(365),
        "3Y": get_change(365*3),
        "5Y": get_change(365*5)
    }