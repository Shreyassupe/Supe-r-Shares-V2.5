from nicegui import ui
# Import basic logic
from logic import (fetch_yf, add_indicators, get_decision, explain_takeaways, 
                   get_pros_cons, get_peers, is_favorite, toggle_favorite, 
                   fetch_fundamentals, fetch_financials, fetch_holders, 
                   backtest_stock, fetch_news, fetch_market_regime) 
from universe import COMPANIES
from theme import frame
from portfolio_manager import add_transaction
import datetime as dt
import pandas as pd

# IMPORT COMPONENT FILE
import detail_page2 as dp2 

def render_detail(ticker: str):
    # 1. Fetch Basic Info
    company_info = next((c for c in COMPANIES if c["ticker"] == ticker), None)
    full_name = company_info["name"] if company_info else ticker
    sector = company_info.get("sector", "Unknown") if company_info else "Unknown"
    market = company_info.get("market", "USA") if company_info else "USA"
    cur = "₹" if market == "INDIA" else "$"

    # 2. Fetch ALL Data (5 Years) for Slider
    end_date = dt.date.today()
    start_date = end_date - dt.timedelta(days=365*5 + 20)
    full_df = fetch_yf(ticker, start_date, end_date)
    
    if not full_df.empty:
        full_df = add_indicators(full_df)

    # 3. Fetch Deep Fundamentals
    info = fetch_fundamentals(ticker)
    financials = fetch_financials(ticker)
    major_holders_df, inst_holders_df = fetch_holders(ticker)
    quote_type = info.get("quoteType", "EQUITY").upper()
    is_etf = quote_type == "ETF"
    
    # 4. Fetch Advanced Metrics for Decision Engine
    roce_data = dp2.calculate_roce(ticker) # Returns dict {'current': '15.2%', ...}
    perf_data = dp2.get_performance_stats(full_df) # Returns dict {'3Y': 12.5, ...}
    market_regime = fetch_market_regime(market)

    with frame(f"Detail - {ticker}"):
        
        if full_df.empty: 
            ui.label(f"No Data Found for {ticker}").classes("text-red-500 text-2xl")
            return

        last = full_df.iloc[-1]
        
        # --- NEW DECISION CALL ---
        sig = get_decision(
            full_df, 
            profile="TRADER", 
            info=info, 
            roce_val=roce_data.get("current"), 
            cagr_val=perf_data.get("3Y"),
            market_regime=market_regime
        )
        
        takeaways = explain_takeaways(full_df)

        # --- A. BUY DIALOG ---
        def open_buy_dialog(current_price):
            with ui.dialog() as dialog, ui.card().classes("bg-slate-900 border border-slate-700 w-96"):
                ui.label(f"Add {ticker} to Portfolio").classes("text-xl font-bold text-white mb-4")
                qty_input = ui.number(label="Shares Bought", value=1).classes("w-full mb-2")
                price_input = ui.number(label="Price", value=current_price).classes("w-full mb-6")
                def save():
                    add_transaction(ticker, qty_input.value, price_input.value)
                    dialog.close(); ui.notify("Added!", color="green")
                ui.button("Add", on_click=save).props("color=green")
            dialog.open()

        # --- B. BACKTEST DIALOG (UNCHANGED) ---
        def run_backtest_ui(df_data):
            with ui.dialog() as dialog, ui.card().classes("bg-slate-900 border border-slate-700 w-full max-w-4xl"):
                with ui.row().classes("w-full justify-between items-center mb-4"):
                    ui.label(f"Strategy Simulation: {ticker} (1 Year)").classes("text-xl font-bold text-white")
                    ui.icon("science").classes("text-purple-400 text-2xl")
                res = backtest_stock(df_data, profile="TRADER")
                if not res or res["Total Trades"] == 0:
                    ui.label("No trades triggered.").classes("text-slate-400 italic")
                else:
                    with ui.grid().classes("grid-cols-2 md:grid-cols-4 gap-4 w-full mb-6"):
                        def b_card(label, val, col):
                            with ui.column().classes("bg-slate-800 p-3 rounded border border-slate-600"):
                                ui.label(label).classes("text-[10px] text-slate-400 uppercase font-bold")
                                ui.label(val).classes(f"text-2xl font-black {col}")
                        ret_col = "text-green-400" if res['Return %'] > 0 else "text-red-400"
                        b_card("Total Return", f"{res['Return %']:.1f}%", ret_col)
                        b_card("Win Rate", f"{res['Win Rate']:.0f}%", "text-blue-400")
                        b_card("Net Profit", f"${res['Final Capital'] - res['Initial Capital']:,.2f}", ret_col)
                        b_card("Final Balance", f"${res['Final Capital']:,.2f}", "text-white")
                    
                    ui.label("Trade History").classes("text-sm font-bold text-white mb-2 uppercase tracking-wider")
                    rows = []
                    for t in res['Trade Log']:
                        d_str = t['Date'].strftime('%Y-%m-%d') if hasattr(t['Date'], 'strftime') else str(t['Date'])
                        p_str = f"${t['Profit']:+,.2f}" if 'Profit' in t else "—"
                        rows.append({'Date': d_str, 'Type': t['Type'], 'Price': f"${t['Price']:.2f}", 'Reason': t.get('Reason', 'Signal'), 'Profit': p_str})
                    rows.reverse()
                    
                    cols = [{'name':'Date', 'label':'DATE', 'field':'Date', 'align':'left'}, {'name':'Type', 'label':'ACTION', 'field':'Type', 'align':'center'}, {'name':'Price', 'label':'PRICE', 'field':'Price', 'align':'right'}, {'name':'Reason', 'label':'REASON', 'field':'Reason', 'align':'left'}, {'name':'Profit', 'label':'PROFIT ($)', 'field':'Profit', 'align':'right'}]
                    table = ui.table(columns=cols, rows=rows).classes("w-full border-slate-700")
                    table.props("dark dense flat")
                    table.add_slot('body-cell-Type', r'''<q-td :props="props"><q-badge :color="props.value === 'BUY' ? 'blue' : 'purple'" :label="props.value" /></q-td>''')
                    table.add_slot('body-cell-Profit', r'''<q-td :props="props" :class="props.value.includes('+') ? 'text-green-400 font-mono font-bold' : (props.value.includes('-') ? 'text-red-400 font-mono font-bold' : 'text-slate-500')">{{ props.value }}</q-td>''')

                ui.button("Close Results", on_click=dialog.close).classes("w-full mt-4 bg-slate-800 hover:bg-slate-700 text-white")
            dialog.open()

        # --- C. HEADER & PRICE ---
        with ui.column().classes("w-full max-w-7xl mx-auto p-4 gap-4"):
            with ui.row().classes("w-full justify-between items-end mb-2"):
                with ui.column().classes("gap-0"):
                    ui.label(full_name).classes("text-3xl md:text-4xl font-black text-white")
                    ui.label(f"{ticker} • {sector} • {market}").classes("text-sm text-slate-400 font-bold")
                
                with ui.row().classes("gap-2"):
                    ui.button("Test Strategy", icon="science", on_click=lambda: run_backtest_ui(full_df)).props("outline dense color=purple-400")
                    def toggle_fav_btn(): toggle_favorite(ticker); fav_btn.text = "Saved" if is_favorite(ticker) else "Favorite"
                    fav_btn = ui.button("Favorite", on_click=toggle_fav_btn).props("outline dense")
                    ui.button("Add to Portfolio", icon="business_center", on_click=lambda: open_buy_dialog(last["close"])).props("dense color=blue-600")

            chg = last["close"] - full_df.iloc[-2]["close"]
            chg_pct = (chg / full_df.iloc[-2]["close"]) * 100
            chg_color = "text-green-400" if chg > 0 else "text-red-400"
            with ui.grid().classes("w-full grid-cols-2 md:grid-cols-4 gap-4"):
                def metric_card(label, val, subval=None, color="text-white"):
                    with ui.card().classes("bg-slate-900 border border-slate-700 p-3"):
                        ui.label(label).classes("text-slate-400 text-[10px] uppercase font-bold")
                        ui.label(val).classes(f"text-xl font-bold {color}")
                        if subval: ui.label(subval).classes(f"text-xs font-bold {color}")
                metric_card("Last Price", f"{cur}{last['close']:.2f}")
                metric_card("Change", f"{chg_pct:+.2f}%", f"{chg:+.2f}", chg_color)
                metric_card("Day High", f"{cur}{last['high']:.2f}", "text-slate-300")
                metric_card("Day Low", f"{cur}{last['low']:.2f}", "text-slate-300")

            # --- D. HIERARCHY ---
            
            # 1. About
            summary = info.get("longBusinessSummary", "No description available.")
            with ui.expansion("About Company", icon="info").classes("w-full bg-slate-900 border border-slate-800 text-slate-300"):
                ui.label(summary).classes("p-4 text-sm text-slate-400 leading-relaxed")

            # 2. Interactive Chart (SLIDER)
            dp2.render_interactive_section(full_df, cur)

            # 3. Quant DNA
            dp2.render_quant_dna_section(ticker, info, full_df)

            # --- 4. NEW ANALYST ACTION GRID (MASTER PLAN IMPLEMENTATION) ---
            ui.label("Analyst Verdict (Quant Engine V2)").classes("text-xl font-bold text-white mt-6")
            with ui.grid().classes("w-full grid-cols-1 md:grid-cols-3 gap-6"):
                
                # CARD 1: THE GAUGE & ARCHETYPE
                score_val = sig.get('Score', 0)
                decision = sig.get('Decision', 'WAIT')
                
                # FIXED COLOR LOGIC: Based on Decision string
                if "BUY" in decision:
                    score_color = "green"
                elif "AVOID" in decision or "SELL" in decision:
                    score_color = "red"
                else:
                    score_color = "orange"
                
                with ui.card().classes(f"bg-gradient-to-br from-{score_color}-900/30 to-slate-900 border border-{score_color}-500 p-6 flex flex-col items-center justify-center text-center"):
                    ui.label("CONVICTION SCORE").classes(f"text-{score_color}-300 text-xs font-bold tracking-widest uppercase mb-2")
                    with ui.row().classes("items-baseline gap-1 justify-center"):
                        ui.label(f"{score_val}").classes("text-6xl font-black text-white")
                        ui.label("/100").classes("text-xl text-slate-400 font-bold")
                    
                    # DECISION & ARCHETYPE (SAFE GET)
                    ui.label(decision).classes(f"text-3xl font-black text-{score_color}-400 uppercase mt-3 leading-none")
                    ui.label(sig.get('Archetype', 'Analysis')).classes("text-slate-100 font-bold text-lg mt-1 italic")

                # CARD 2: REASONING (CENTER CARD - Updated with Metrics)
                with ui.card().classes("bg-slate-900 border border-slate-700 p-5"):
                    ui.label("Strategic Analysis").classes("text-xs font-bold text-blue-400 uppercase mb-3")
                    # Clean Bullet Points with Logic Data (ROCE, CAGR etc)
                    ui.markdown(sig.get('Reason', 'No analysis available.')).classes("text-sm text-slate-200 leading-relaxed font-medium space-y-2")
                    
                    with ui.row().classes("w-full gap-2 mt-4 pt-4 border-t border-slate-800"):
                        m_stat = market_regime.get("status", "NEUTRAL")
                        m_col = "green" if "BULL" in m_stat else ("red" if "BEAR" in m_stat else "orange")
                        ui.badge(f"MARKET: {m_stat}", color=m_col).props("outline").classes("text-[10px] font-bold")
                        
                        ui.badge(f"PROFILE: {sig.get('Framework', 'TRADER')}", color="blue-grey").props("outline").classes("text-[10px] font-bold")

                # CARD 3: SCORE BREAKDOWN (RIGHT CARD - Clean Progress Bars)
                with ui.card().classes("bg-slate-900 border border-slate-700 p-5 flex flex-col justify-center"):
                    ui.label("Factor Scorecard").classes("text-xs font-bold text-slate-400 uppercase mb-4")
                    
                    factors = sig.get('Factors', {})
                    if factors:
                        for key, val in factors.items():
                            if key == "Market": continue 
                            
                            color = "green" if val >= 70 else ("orange" if val >= 40 else "red")
                            with ui.column().classes("w-full gap-1 mb-3"):
                                with ui.row().classes("w-full justify-between"):
                                    ui.label(key).classes("text-xs font-bold text-slate-300")
                                    ui.label(str(val)).classes(f"text-xs font-black text-{color}-400")
                                
                                # Removed label inside progress bar for cleaner look
                                ui.linear_progress(val/100, show_value=False).props(f"color={color} track-color=grey-9 rounded size=8px").classes("rounded-full")

            # 5. Fundamentals (RESTORED BIG TABLE)
            dp2.render_fundamentals_section(ticker, info, is_etf, cur)

            # 6. Financial Charts & Ownership
            dp2.render_financials_ownership(financials, major_holders_df, is_etf)

            # 7. Trailing Returns (Performance)
            dp2.render_performance_table(full_df)

            # 8. Analyst Price Target (Fixed & Improved)
            if not is_etf and info.get("targetMeanPrice"):
                with ui.card().classes("w-full bg-slate-900 border border-slate-700 p-4 mt-6"):
                    ui.label("Wall St. Price Target").classes("text-sm font-bold text-slate-300 uppercase mb-4")
                    target = info.get("targetMeanPrice")
                    current = last["close"] 
                    upside = ((target - current) / current) * 100
                    up_color = "text-green-400" if upside > 0 else "text-red-400"
                    with ui.row().classes("w-full items-baseline gap-4"):
                        ui.label(f"{cur}{target:,.2f}").classes("text-4xl font-black text-white")
                        ui.label(f"{upside:+.1f}% potential").classes(f"text-lg font-bold {up_color}")
                    
                    low = info.get("targetLowPrice", current * 0.8); high = info.get("targetHighPrice", current * 1.2)
                    range_span = high - low if high > low else 1
                    pos_pct = min(max((current - low) / range_span * 100, 0), 100)

                    ui.html(f'''
                        <div style="width:100%; height:12px; background:#1e293b; border-radius:6px; position:relative; margin-top:15px; overflow:hidden;">
                            <div style="position:absolute; left:0; top:0; height:100%; width:100%; background: linear-gradient(90deg, #ef4444 0%, #eab308 50%, #22c55e 100%); opacity:0.4;"></div>
                            <div style="position:absolute; left:{pos_pct}%; top:-4px; width:4px; height:20px; background:white; box-shadow: 0 0 8px white, 0 0 4px #22c55e;"></div>
                        </div>
                        <div style="display:flex; justify-content:space-between; margin-top:8px; color:#64748b; font-size:11px; font-weight:bold;">
                            <span>Low: {cur}{low:,.0f}</span> <span>▲ Now: {cur}{current:,.0f}</span> <span>High: {cur}{high:,.0f}</span>
                        </div>
                    ''', sanitize=False)

            # 10. Peers & Patterns
            dp2.render_peers_patterns(ticker, sector, full_df, start_date, end_date, market)

            # 11. Future Simulator
            dp2.render_monte_carlo_section(full_df, cur)

            # 12. Risk Plan
            ui.label("Trade Risk Plan").classes("text-xl font-bold text-white mt-6")
            with ui.grid().classes("w-full grid-cols-2 md:grid-cols-4 gap-4"):
                def stat_card(label, value, color="text-white", icon=None):
                    with ui.card().classes("bg-slate-900 border border-slate-700 p-4 flex flex-row items-center gap-3"):
                        if icon: ui.icon(icon).classes(f"text-2xl {color} opacity-50")
                        with ui.column().classes("gap-0"):
                            ui.label(label).classes("text-slate-400 text-[10px] uppercase font-bold")
                            ui.label(str(value)).classes(f"text-xl font-black {color}")
                stat_card("Volatility (ATR)", f"{sig.get('ATR', 0):.2f}", icon="water")
                stat_card("Stop Loss Level", f"{cur}{sig.get('Stop', 0):.2f}" if sig.get('Stop') else "N/A", "text-red-400", icon="security")
                stat_card("Target Level", f"{cur}{sig.get('Target', 0):.2f}" if sig.get('Target') else "N/A", "text-green-400", icon="gps_fixed")
                stat_card("RSI Momentum", f"{sig.get('RSI', 50):.0f}", "text-yellow-400" if sig.get('RSI', 50)>70 or sig.get('RSI', 50)<30 else "text-blue-400", icon="speed")

            # 13. News
            ui.label("Latest Headlines").classes("text-xl font-bold text-white mt-6")
            news_items = fetch_news(ticker, limit=4)
            if news_items:
                with ui.grid().classes("w-full grid-cols-1 md:grid-cols-2 gap-3"):
                    for item in news_items:
                        if item.get('title'):
                            with ui.card().classes("bg-slate-900 border border-slate-700 p-3 hover:bg-slate-800 transition-colors h-full"):
                                with ui.column().classes("justify-between h-full gap-2"):
                                    with ui.column().classes("gap-1"):
                                        ui.label(item.get('publisher')).classes("text-[10px] text-blue-400 font-bold uppercase")
                                        ui.link(item.get('title'), item.get('link'), new_tab=True).classes("text-white font-bold text-sm leading-tight no-underline hover:text-blue-300")
                                    ui.label(dt.datetime.fromtimestamp(item.get('providerPublishTime', 0)).strftime('%Y-%m-%d %H:%M')).classes("text-[10px] text-slate-500 text-right w-full")
            else:
                ui.label("No recent news found.").classes("text-slate-500 italic")