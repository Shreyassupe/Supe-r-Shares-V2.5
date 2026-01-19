from nicegui import ui, app, run 
from logic import (add_indicators, get_decision, fetch_fundamentals, 
                   is_favorite, toggle_favorite, fetch_news, fetch_market_regime)
from logic2 import calculate_roce, get_performance_stats
from universe import COMPANIES
from theme import frame
from portfolio_manager import add_transaction, get_portfolio_tickers
import pandas as pd
import datetime as dt
import yfinance as yf
import contextlib
import io
import numpy as np
import plotly.express as px 
import time

# --- 1. ROBUST BATCHED FETCHER ---
def fetch_and_process_batches(companies, market_regime):
    if not companies: return []
    tickers_map = {c['ticker']: c for c in companies}
    all_tickers = list(tickers_map.keys())
    batch_size = 15
    batches = [all_tickers[i:i + batch_size] for i in range(0, len(all_tickers), batch_size)]
    results = []
    start = dt.date.today() - dt.timedelta(days=400) 

    for batch in batches:
        try:
            time.sleep(0.2) 
            with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
                data = yf.download(batch, start=start, group_by='ticker', progress=False, threads=True)
            if data.empty: continue
            
            for t in batch:
                try:
                    c = tickers_map.get(t)
                    if len(batch) == 1: df = data.copy()
                    else:
                        if t not in data.columns.levels[0]: continue
                        df = data[t].copy()
                    
                    df.columns = [str(col).lower() for col in df.columns]
                    if 'close' not in df.columns and 'adj close' in df.columns: df = df.rename(columns={'adj close': 'close'})
                    df = df.ffill().dropna(subset=['close'])
                    if len(df) < 50: continue
                    
                    df = add_indicators(df)
                    sig = get_decision(df, profile="TRADER", owned=False, info=None, cagr_val=100, market_regime=market_regime)
                    
                    last = df.iloc[-1]
                    prev = df.iloc[-2] if len(df) > 1 else last
                    curr_price = last['close']
                    chg = curr_price - prev['close']
                    pct_chg = (chg / prev['close']) * 100 if prev['close'] != 0 else 0
                    ma20 = last.get("ma20", curr_price)
                    dist_ma20 = ((curr_price - ma20) / ma20) * 100 if ma20 else 0
                    
                    score = sig["Score"]
                    decision = "WAIT"
                    rsi = sig.get("RSI", 50)
                    vol = sig.get("Volatility", "Normal")

                    if score >= 75: decision = "BUY"
                    elif score >= 50: decision = "WAIT"
                    else: decision = "AVOID"

                    if decision == "AVOID" and rsi < 35: decision = "WATCH"
                    elif decision == "BUY" and vol == "High": decision = "SWING"

                    results.append({
                        "Ticker": t, "Company": c["name"], "Sector": c.get("sector", "Other"),
                        "Decision": decision, "Reason": sig["Reason"], "Conf": sig.get("Conf", "Medium"),
                        "Entry": sig.get("Entry", "—"), "Stop": sig["Stop"], "Target": sig["Target"],
                        "Framework": sig["Framework"], "Score": score, "Short": sig.get("Short", "Neutral"),
                        "Long": sig.get("Long", "Neutral"), "Volatility": vol, "Last Close": curr_price,
                        "Change": chg, "Change%": pct_chg, "Volume": last.get("volume", 0),
                        "ATR": sig["ATR"], "RSI": sig["RSI"], "DistMA20": dist_ma20
                    })
                except: continue
        except: continue
    return results

async def accurate_score_universe(companies, lookback_days, profile):
    market_name = app.storage.user.get("market", "USA")
    market_regime = fetch_market_regime(market_name)
    rows = await run.io_bound(fetch_and_process_batches, companies, market_regime)
    return pd.DataFrame(rows) if rows else pd.DataFrame()

# --- 2. RENDER UI ---
def render_home():
    if "market" not in app.storage.user: app.storage.user["market"] = "USA"
    if "home_sort" not in app.storage.user: app.storage.user["home_sort"] = {"col": "Score", "asc": False}
    if "sector_filter" not in app.storage.user: app.storage.user["sector_filter"] = "All"
    if "profile" not in app.storage.user: app.storage.user["profile"] = "TRADER"
    
    market = app.storage.user["market"]
    cur = "₹" if market == "INDIA" else "$"
    sort_state = app.storage.user["home_sort"]

    GRID_COLS = "90px 90px 180px 80px 80px 70px 90px 90px 60px 110px 75px 75px 60px 80px 80px 80px"
    GRID_CSS = f"display: grid; grid-template-columns: {GRID_COLS}; gap: 6px; align-items: center; padding-left: 4px; padding-right: 4px;"
    ROW_WIDTH = "min-w-[1450px]"

    with frame(f"Home"): 
        
        def open_buy_dialog(ticker, price_val):
            try: clean_price = float(price_val)
            except: clean_price = 0.0
            with ui.dialog() as dialog, ui.card().classes("bg-slate-900 border border-slate-700 w-96"):
                ui.label(f"Add {ticker}").classes("text-xl font-bold text-white mb-4")
                qty_input = ui.number(label="Shares", value=1, min=0.01).classes("w-full mb-2")
                price_input = ui.number(label="Price", value=clean_price, format="%.2f").classes("w-full mb-6")
                def save():
                    add_transaction(ticker, qty_input.value, price_input.value)
                    dialog.close(); ui.notify(f"Added {ticker}", color="green"); render_dashboard.refresh()
                ui.button("Add", on_click=save).props("color=green")
            dialog.open()

        def open_legend():
            with ui.dialog() as d, ui.card().classes("bg-slate-900 border border-slate-700 p-6 w-[600px]"):
                ui.label("Analyst Verdict Legend").classes("text-xl font-bold text-white mb-6")
                def item(title, desc, color):
                    with ui.row().classes("items-start gap-4 mb-4 w-full"):
                        ui.badge(title, color=color).classes("w-24 text-center font-bold text-md py-1")
                        ui.label(desc).classes("text-sm text-slate-300 flex-1 leading-relaxed")
                item("INVEST", "Strong Buy. High Score + Positive Growth.", "green")
                item("BUY", "Strong Technical Trend. Good for trading.", "green")
                item("SWING", "Price is up, but Fundamentals are weak. Short Term Only.", "cyan")
                item("WATCH", "Great Company (High Growth), but Price is dropping.", "blue")
                item("WAIT", "Neutral. No clear signal.", "orange")
                item("AVOID", "Sell/Avoid. Broken Trend or Bad Data.", "red")
                ui.button("Close", on_click=d.close).classes("w-full mt-6 bg-slate-800 text-slate-400 hover:text-white")
            d.open()

        @ui.refreshable
        def render_dashboard():
            current_filter = app.storage.user.get("sector_filter", "All")
            search_val = app.storage.user.get("search_ticker")
            
            # --- FIX: Removed top padding (pt-0) to remove the black bar ---
            content = ui.column().classes("w-full gap-6 px-4 pb-4 pt-0")

            async def run_calculation():
                filtered = [c for c in COMPANIES if str(c.get("market", "USA")).upper() == market]
                if current_filter and current_filter != "All": 
                    filtered = [c for c in filtered if c.get("sector") == current_filter]
                if search_val:
                    s_val = search_val.split(" - ")[0]
                    filtered = [c for c in filtered if c["ticker"] == s_val]
                
                df = await accurate_score_universe(filtered, 120, app.storage.user["profile"])
                
                content.clear()
                if df.empty:
                    with content: ui.label(f"No data available.").classes("text-red-400 text-xl")
                    return

                with content:
                    # 1. Metrics Banner
                    advancing = df[df['Change']>0].shape[0]
                    declining = df[df['Change']<0].shape[0]
                    
                    with ui.card().classes("w-full bg-slate-800 border-l-4 border-blue-500 p-4 shadow-lg mb-4 rounded-t-none"): # Added rounded-t-none for seamless look
                        with ui.row().classes("w-full justify-between items-center wrap"):
                            with ui.column().classes("gap-0"):
                                ui.label(f"Market Regime: {market}").classes("text-xl font-black text-white")
                                ui.label(f"{len(df)} Assets Active • {advancing} Advancing").classes("text-sm font-bold text-blue-300 font-mono")
                            with ui.row().classes("gap-2"):
                                ui.badge(f"{advancing} Up", color="green").props("outline")
                                ui.badge(f"{declining} Down", color="red").props("outline")

                    # 2. Sector Chips
                    if current_filter == "All" and "Sector" in df.columns:
                        sector_perf = df.groupby("Sector")['Change%'].median().sort_values(ascending=False)
                        with ui.element('div').style('display: grid; grid-template-columns: repeat(auto-fill, minmax(130px, 1fr)); gap: 12px; width: 100%; margin-bottom: 24px;'):
                            with ui.card().classes("bg-blue-900/40 border border-blue-500 p-3 rounded-lg w-full h-full min-h-[90px] flex flex-col justify-center items-center shadow-md"):
                                ui.label("ALL SECTORS").classes("text-[10px] font-bold text-blue-300 tracking-wider uppercase")
                                ui.icon("apps").classes("text-xl text-white mt-1")
                            
                            for sec, val in sector_perf.items():
                                col_cls = "text-green-400" if val > 0 else ("text-red-400" if val < 0 else "text-slate-400")
                                border_cls = "border-green-500/30" if val > 0 else ("border-red-500/30" if val < 0 else "border-slate-700")
                                bg_cls = "bg-green-500/5" if val > 0 else ("bg-red-500/5" if val < 0 else "bg-slate-800/50")
                                def on_sec_click(s=sec):
                                    app.storage.user["sector_filter"] = s
                                    render_dashboard.refresh()
                                with ui.card().classes(f"{bg_cls} border {border_cls} p-3 rounded-lg w-full h-full min-h-[90px] hover:bg-slate-700 transition-all cursor-pointer shadow-sm flex flex-col justify-between").on("click", on_sec_click):
                                    ui.label(sec).classes("text-[10px] uppercase font-bold text-slate-400 tracking-wider truncate w-full")
                                    with ui.row().classes("items-center gap-1 mt-auto"):
                                        ui.icon("trending_up" if val > 0 else "trending_down").classes(f"text-sm {col_cls}")
                                        ui.label(f"{val:+.2f}%").classes(f"text-lg font-black {col_cls} leading-none")
                    elif current_filter != "All":
                        with ui.row().classes("w-full justify-center mb-6"):
                            def clear_filter():
                                app.storage.user["sector_filter"] = "All"
                                render_dashboard.refresh()
                            ui.button(f"Viewing {current_filter} - Click to Clear", icon="close", on_click=clear_filter).props("outline rounded color=blue-400")

                    with ui.row().classes("w-full items-center gap-2 mb-4"):
                        ui.label("Top Opportunities").classes("text-2xl font-black text-white tracking-tight")
                        ui.button(icon="help_outline", on_click=open_legend).props("flat dense round color=slate-400")

                    df_sorted = df.sort_values(by="Score", ascending=False)
                    with ui.element('div').style('display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; width: 100%; margin-bottom: 24px;'):
                        for _, row in df_sorted.head(4).iterrows():
                            decision = row["Decision"]
                            if "SWING" in decision: bg_cls, d_col = "bg-gradient-to-br from-cyan-900/50 to-slate-900 border-cyan-500", "cyan"
                            elif "BUY" in decision or "INVEST" in decision: bg_cls, d_col = "bg-gradient-to-br from-green-900/50 to-slate-900 border-green-500", "green"
                            elif "WATCH" in decision: bg_cls, d_col = "bg-gradient-to-br from-blue-900/50 to-slate-900 border-blue-500", "blue"
                            elif "WAIT" in decision: bg_cls, d_col = "bg-gradient-to-br from-orange-900/40 to-slate-900 border-orange-500/50", "orange"
                            else: bg_cls, d_col = "bg-gradient-to-br from-red-900/50 to-slate-900 border-red-500", "red"

                            chg = row['Change']; chg_pct = row['Change%']
                            arrow = "▲" if chg > 0 else "▼"; txt_col = "text-green-400" if chg > 0 else "text-red-400"
                            
                            with ui.card().classes(f"p-5 border shadow-xl {bg_cls} h-full min-h-[280px] flex flex-col justify-between hover:scale-[1.02] transition-transform duration-200 relative overflow-hidden"):
                                with ui.column().classes("w-full gap-0"):
                                    with ui.row().classes("w-full justify-between items-center no-wrap gap-2"):
                                        ui.label(row["Ticker"]).classes("text-2xl font-black text-white tracking-tight truncate")
                                        ui.label(f"{cur}{row['Last Close']:.2f}").classes("text-md font-bold text-white/90 font-mono whitespace-nowrap")
                                    ui.label(row["Company"]).classes("text-xs font-medium text-slate-400 truncate w-full mb-3")
                                    ui.label(f"{arrow} {chg:+.2f} ({chg_pct:+.2f}%)").classes(f"text-sm font-bold font-mono {txt_col}")
                                ui.separator().classes("bg-white/10 my-2")
                                with ui.column().classes("w-full gap-2 mb-2"):
                                    with ui.row().classes("w-full justify-between items-center"):
                                        ui.label("Trend").classes("text-[10px] font-bold text-slate-400 uppercase")
                                        ui.label(f"{row.get('DistMA20',0):+.1f}%").classes(f"text-xs font-bold text-white")
                                    with ui.row().classes("w-full justify-between items-center"):
                                        ui.badge(decision, color=d_col).props("outline").classes("font-bold text-sm px-2")
                                        with ui.row().classes("gap-1 items-center"):
                                            ui.label("SCORE").classes("text-[10px] font-bold text-slate-500")
                                            ui.label(f"{row['Score']:.0f}").classes("text-lg font-black text-white font-mono")
                                ui.button("Open", on_click=lambda t=row["Ticker"]: ui.navigate.to(f'/detail/{t}')).props("flat dense").classes("w-full mt-auto text-white/50 hover:text-white hover:bg-white/10")

                    with ui.tabs().classes('w-full text-white bg-slate-800/50 rounded-t-lg') as tabs:
                        tab_list = ui.tab('List View', icon='list')
                        tab_map = ui.tab('Market Map', icon='dashboard')

                    with ui.tab_panels(tabs, value=tab_list).classes('w-full bg-transparent'):
                        with ui.tab_panel(tab_list).classes("p-0"):
                            tdf = df.fillna(0).copy()
                            owned_tickers = get_portfolio_tickers()
                            tdf['Ticker'] = tdf['Ticker'].astype(str)
                            tdf['is_fav'] = tdf['Ticker'].apply(is_favorite)
                            tdf['is_owned'] = tdf['Ticker'].apply(lambda t: t in owned_tickers)
                            
                            rank_map = {"BUY": 4, "INVEST": 4, "SWING": 3, "WATCH": 2, "WAIT": 1, "AVOID": 0}
                            if sort_state['col'] in ["Decision", "Framework"]:
                                tdf["_Rank"] = tdf[sort_state['col']].map(lambda x: rank_map.get(x, 0))
                                tdf = tdf.sort_values(by="_Rank", ascending=sort_state['asc'])
                            elif sort_state['col'] in tdf.columns:
                                tdf = tdf.sort_values(by=sort_state['col'], ascending=sort_state['asc'])

                            def handle_sort(col_name):
                                if sort_state['col'] == col_name: sort_state['asc'] = not sort_state['asc']
                                else: sort_state['col'] = col_name; sort_state['asc'] = col_name not in ["Score", "Last Close", "Change%", "Decision", "Framework"]
                                app.storage.user["home_sort"] = sort_state; render_dashboard.refresh()

                            with ui.scroll_area().classes('h-[800px] w-full'):
                                with ui.element('div').classes(f'w-full border-b border-slate-600 bg-slate-900 sticky top-0 z-10 py-3 shadow-md {ROW_WIDTH}').style(GRID_CSS):
                                    def header(label, col_db=None, align="left"):
                                        base = f'text-{align} text-xs font-bold tracking-wider uppercase text-slate-400 select-none truncate'
                                        if col_db:
                                            color = "text-blue-400" if sort_state['col'] == col_db else "hover:text-slate-200 cursor-pointer"
                                            arrow = " ▼" if sort_state['col'] == col_db and not sort_state['asc'] else (" ▲" if sort_state['col'] == col_db else "")
                                            with ui.element('div').classes(f"{base} {color}").on('click', lambda: handle_sort(col_db)): ui.label(label + arrow)
                                        else: ui.label(label).classes(base)
                                    header('ACTIONS', align="center"); header('TICKER', 'Ticker'); header('COMPANY', 'Company'); header('PRICE', 'Last Close', align="right"); header('CHANGE', 'Change', align="right"); header('%', 'Change%', align="right"); header('DECISION', 'Decision', align="center"); header('PROFILE', 'Framework', align="center"); header('CONF', 'Conf', align="center"); header('WATCH LEVEL', 'Entry'); header('STOP', 'Stop', align="right"); header('TARGET', 'Target', align="right"); header('SCORE', 'Score', align="center"); header('SHORT', 'Short'); header('LONG', 'Long'); header('VOLATILITY', 'Volatility')

                                for _, row in tdf.iterrows():
                                    price_str = f"{cur}{row['Last Close']:,.2f}"
                                    chg = row['Change']; chg_pct = row['Change%']
                                    arrow = "▲" if chg > 0 else "▼"; chg_color = "text-green-400" if chg > 0 else "text-red-400"
                                    chg_str = f"{arrow} {chg:.2f}"; pct_str = f"{chg_pct:+.2f}%"
                                    
                                    decision = row['Decision']
                                    if "SWING" in decision: dec_color = "cyan"
                                    elif "BUY" in decision or "INVEST" in decision: dec_color = "green"
                                    elif "WATCH" in decision: dec_color = "blue"
                                    elif "WAIT" in decision: dec_color = "orange"
                                    else: dec_color = "red"

                                    fw = row['Framework']; fw_color = "green" if fw == "INVEST" else ("red" if fw == "AVOID" else "orange")
                                    stop_str = f"{cur}{row['Stop']:.2f}" if row['Stop'] > 0 else "—"
                                    tgt_str = f"{cur}{row['Target']:.2f}" if row['Target'] > 0 else "—"
                                    
                                    with ui.element('div').classes(f'w-full hover:bg-white/5 transition-colors border-b border-slate-800 py-1 {ROW_WIDTH}').style(GRID_CSS):
                                        with ui.row().classes('justify-center gap-1 no-wrap items-center h-full'):
                                            ui.button(icon='star' if row['is_fav'] else 'star_border', color='amber' if row['is_fav'] else 'grey', on_click=lambda t=row['Ticker']: (toggle_favorite(t), render_dashboard.refresh())).props('flat dense round size=sm')
                                            pf_col = 'blue-500' if row['is_owned'] else 'grey-700'; pf_props = 'flat dense round size=sm' if row['is_owned'] else 'outline dense round size=sm'
                                            ui.button(icon='business_center', color=pf_col, on_click=lambda t=row['Ticker'], p=row['Last Close']: open_buy_dialog(t, p)).props(pf_props)
                                        
                                        ui.link(row['Ticker'], f"/detail/{row['Ticker']}").classes('text-base font-bold text-blue-400 no-underline hover:text-white truncate')
                                        ui.label(str(row['Company'])).classes('text-xs text-slate-300 truncate font-medium')
                                        ui.label(price_str).classes('text-right font-mono text-sm text-white')
                                        ui.label(chg_str).classes(f'{chg_color} text-right font-mono text-sm font-bold')
                                        ui.label(pct_str).classes(f'{chg_color} text-right font-mono text-sm')
                                        with ui.row().classes('justify-center'): ui.badge(decision, color=dec_color).props('outline').classes('font-bold text-[10px] px-2 py-0.5')
                                        with ui.row().classes('justify-center'): ui.badge(fw, color=fw_color).classes('text-[10px] px-2 py-0.5 font-bold text-white')
                                        ui.label(str(row['Conf'])).classes('text-center text-xs text-white')
                                        ui.label(str(row['Entry']) if row['Entry'] else "—").classes('text-left text-xs text-slate-400 truncate')
                                        ui.label(stop_str).classes('text-right font-mono text-xs text-red-400')
                                        ui.label(tgt_str).classes('text-right font-mono text-xs text-green-400')
                                        ui.label(f"{row['Score']:.0f}").classes('text-center text-base font-bold text-white')
                                        ui.label(str(row['Short'])).classes('text-left text-xs text-slate-400 truncate')
                                        ui.label(str(row['Long'])).classes('text-left text-xs text-slate-400')
                                        ui.label(str(row['Volatility'])).classes('text-left text-xs text-slate-400')

                        with ui.tab_panel(tab_map).classes("p-0 min-h-[650px]"):
                            try:
                                df_map = df.copy()
                                df_map["Size"] = df_map["Volume"].replace(0, 1)
                                df_map["MapLabel"] = df_map.apply(lambda x: f"<b>{x['Ticker']}</b><br>{x['Change%']:+.2f}%", axis=1)
                                fig = px.treemap(df_map, path=[px.Constant(market), 'Sector', 'Ticker'], values='Size', color='Change%', color_continuous_scale=[(0.0, '#F63538'), (0.5, '#303030'), (1.0, '#30CC5A')], range_color=[-3, 3], custom_data=['Company', 'Last Close', 'Decision'])
                                fig.update_traces(text=df_map["MapLabel"], textinfo="text", hovertemplate=f"<b>%{{label}}</b><br>%{{customdata[0]}}<br>Price: {cur}%{{customdata[1]}}<br>Signal: %{{customdata[2]}}<extra></extra>", textposition="middle center", textfont=dict(family="Inter", size=14, color="white"))
                                fig.update_layout(margin=dict(t=0, l=0, r=0, b=0), paper_bgcolor="#0f172a", plot_bgcolor="#0f172a", coloraxis_showscale=False)
                                plot = ui.plotly(fig).classes("w-full h-[800px] rounded-lg border border-slate-700 shadow-2xl")
                                plot.on('plotly_click', lambda e: ui.navigate.to(f'/detail/{e.args["points"][0]["label"]}') if 'points' in e.args and 'label' in e.args['points'][0] and e.args['points'][0]['label'] in df_map['Ticker'].values else None)
                            except:
                                ui.label("Heatmap data insufficient.").classes("text-slate-500 italic")

            with content:
                ui.spinner("dots").classes("size-10 self-center text-slate-500")
                ui.timer(0.1, lambda: run_calculation(), once=True)

        render_dashboard()