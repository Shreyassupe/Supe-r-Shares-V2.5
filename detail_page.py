from nicegui import ui
from logic import (fetch_yf, add_indicators, get_decision, detect_patterns, 
                   explain_takeaways, get_pros_cons, get_peers, is_favorite, 
                   toggle_favorite, fetch_fundamentals, fetch_financials, fetch_holders)
from universe import COMPANIES
from theme import frame
from portfolio_manager import add_transaction # <--- Import this
import plotly.graph_objects as go
import datetime as dt
import numpy as np
import pandas as pd

def render_detail(ticker: str):
    company_info = next((c for c in COMPANIES if c["ticker"] == ticker), None)
    full_name = company_info["name"] if company_info else ticker
    sector = company_info.get("sector", "Unknown") if company_info else "Unknown"
    market = company_info.get("market", "USA") if company_info else "USA"
    cur = "₹" if market == "INDIA" else "$"

    with frame(f"Detail - {ticker}"):
        
        # --- 1. POPUP DIALOG FOR PORTFOLIO ---
        def open_buy_dialog(current_price):
            with ui.dialog() as dialog, ui.card().classes("bg-slate-900 border border-slate-700 w-96"):
                ui.label(f"Add {ticker} to Portfolio").classes("text-xl font-bold text-white mb-4")
                
                qty_input = ui.number(label="Shares Bought", value=1, min=0.01).classes("w-full mb-2")
                price_input = ui.number(label="Avg Price", value=current_price, format="%.2f").classes("w-full mb-6")
                
                def save():
                    add_transaction(ticker, qty_input.value, price_input.value)
                    dialog.close()
                    
                with ui.row().classes("w-full justify-end"):
                    ui.button("Cancel", on_click=dialog.close).props("flat color=grey")
                    ui.button("Add to Portfolio", on_click=save).props("color=green")
            dialog.open()
        
        # --- 2. Main UI ---
        with ui.column().classes("w-full max-w-7xl mx-auto p-4 gap-4"):
            
            end = dt.date.today()
            start = end - dt.timedelta(days=400)
            df = fetch_yf(ticker, start, end)
            
            info = fetch_fundamentals(ticker)
            financials = fetch_financials(ticker)
            major_holders_df, inst_holders_df = fetch_holders(ticker)
            
            quote_type = info.get("quoteType", "EQUITY").upper()
            is_etf = quote_type == "ETF"
            
            if df.empty: 
                ui.label(f"No Data Found for {ticker}").classes("text-red-500 text-2xl")
                return
            
            df = add_indicators(df)
            last = df.iloc[-1]
            prev = df.iloc[-2]
            sig = get_decision(df)
            takeaways = explain_takeaways(df)
            pro_con = get_pros_cons(df)
            
            # --- Formatters (Same as before) ---
            def fmt_num_safe(key, prefix="", suffix=""):
                val = info.get(key)
                if val is None or not isinstance(val, (int, float)): return "—"
                try:
                    if abs(val) > 1e12: return f"{prefix}{val/1e12:.2f}T{suffix}"
                    if abs(val) > 1e9: return f"{prefix}{val/1e9:.2f}B{suffix}"
                    if abs(val) > 1e6: return f"{prefix}{val/1e6:.2f}M{suffix}"
                    return f"{prefix}{val:.2f}{suffix}"
                except: return "—"

            def fmt_pct_safe(key):
                val = info.get(key)
                if val is None or not isinstance(val, (int, float)): return "—"
                return f"{val*100:.2f}%"

            def fmt_ratio_safe(key):
                val = info.get(key)
                if val is None or not isinstance(val, (int, float)): return "—"
                return f"{val:.2f}"

            # --- 3. Header Buttons ---
            with ui.row().classes("w-full justify-between items-end mb-2"):
                with ui.column().classes("gap-0"):
                    ui.label(full_name).classes("text-3xl md:text-4xl font-black text-white leading-tight")
                    ui.label(f"{ticker} • {sector} • {market} ({quote_type})").classes("text-sm text-slate-400 font-bold")
                
                with ui.row().classes("gap-2"):
                    # FAVORITE BUTTON
                    def toggle_fav_btn():
                        toggle_favorite(ticker)
                        update_fav_btn()
                        
                    def update_fav_btn():
                        is_fav = is_favorite(ticker)
                        fav_btn.props(f"icon={'star' if is_fav else 'star_border'} color={'amber' if is_fav else 'grey'}")
                        fav_btn.text = "Saved" if is_fav else "Favorite"
                        
                    fav_btn = ui.button("Favorite", on_click=toggle_fav_btn).props("outline dense")
                    update_fav_btn()

                    # PORTFOLIO BUTTON (NEW)
                    ui.button("Add to Portfolio", icon="business_center", on_click=lambda: open_buy_dialog(last["close"])).props("dense color=blue-600")

            # --- 4. Price Cards ---
            chg = last["close"] - prev["close"]
            chg_pct = (chg / prev["close"]) * 100
            chg_color = "text-green-400" if chg > 0 else "text-red-400"
            
            with ui.grid().classes("w-full grid-cols-2 md:grid-cols-4 gap-4"):
                def metric_card(label, val, subval=None, color="text-white"):
                    with ui.card().classes("bg-slate-900 border border-slate-700 p-3"):
                        ui.label(label).classes("text-slate-400 text-[10px] uppercase font-bold")
                        ui.label(val).classes(f"text-xl font-bold {color}")
                        if subval:
                            ui.label(subval).classes(f"text-xs font-bold {color}")
                            
                metric_card("Last Price", f"{cur}{last['close']:.2f}")
                metric_card("Change", f"{chg_pct:+.2f}%", f"{chg:+.2f}", chg_color)
                metric_card("Day High", f"{cur}{last['high']:.2f}", color="text-slate-300")
                metric_card("Day Low", f"{cur}{last['low']:.2f}", color="text-slate-300")

            # --- 5. Signal (Universal Gradients) ---
            with ui.grid().classes("w-full grid-cols-1 md:grid-cols-2 gap-4"):
                decision = sig['Decision']
                
                if decision == "BUY":
                    dec_bg = "bg-gradient-to-br from-green-900/50 to-slate-900"
                    dec_border = "border-green-500"
                    dec_text = "text-green-300"
                elif decision == "WAIT":
                    dec_bg = "bg-gradient-to-br from-yellow-900/40 to-slate-900"
                    dec_border = "border-yellow-600/50"
                    dec_text = "text-yellow-300"
                else: 
                    dec_bg = "bg-gradient-to-br from-red-900/50 to-slate-900"
                    dec_border = "border-red-500"
                    dec_text = "text-red-300"
                
                with ui.card().classes(f"{dec_bg} border {dec_border} p-4"):
                    ui.label("Action Signal").classes(f"{dec_text} text-xs font-bold uppercase tracking-widest")
                    with ui.row().classes("items-baseline gap-3"):
                        ui.label(decision).classes("text-4xl font-black text-white")
                        ui.label(f"({sig['Conf']} Conf.)").classes(f"text-lg font-bold {dec_text}")
                    if sig['Entry']: 
                        ui.separator().classes("bg-white/10 my-2")
                        ui.label(f"Hint: {sig['Entry']}").classes("text-white italic text-sm font-medium")

                with ui.card().classes("bg-slate-900 border border-slate-700 p-4"):
                    ui.label("Analysis Summary").classes("text-slate-400 text-xs font-bold uppercase mb-1")
                    ui.markdown(f"""
                    - **Short:** {takeaways['Short']}
                    - **Medium:** {takeaways['Medium']}
                    - **Long:** {takeaways['Long']}
                    - **Vol:** {sig['Volatility']}
                    """).classes("text-sm leading-tight")

            # --- 6. Fundamentals ---
            ui.label(f"Fundamentals ({'ETF Protocol' if is_etf else 'Finviz Protocol'})").classes("text-lg font-bold text-white mt-2")
            with ui.card().classes("w-full bg-slate-900 border border-slate-700 p-0"):
                with ui.grid().classes("grid-cols-2 sm:grid-cols-3 md:grid-cols-6 w-full gap-px bg-slate-700"):
                    def f_item(label, value, color="text-white"):
                        with ui.column().classes("bg-slate-900 p-2 justify-center h-full"):
                            ui.label(label).classes("text-[9px] uppercase font-bold text-slate-400 tracking-wider truncate w-full")
                            ui.label(str(value)).classes(f"text-xs md:text-sm font-bold {color} truncate w-full")

                    if is_etf:
                        f_item("Net Assets", fmt_num_safe("totalAssets", prefix=cur))
                        f_item("NAV", fmt_num_safe("navPrice", prefix=cur))
                        f_item("Yield", fmt_pct_safe("yield"), "text-green-300")
                        f_item("Expense Ratio", fmt_pct_safe("annualReportExpenseRatio"), "text-red-300")
                        f_item("Beta (3Y)", fmt_ratio_safe("beta3Year"))
                        f_item("Category", info.get("category", "—"))
                        f_item("YTD Return", fmt_pct_safe("ytdReturn"))
                        f_item("3Y Return", fmt_pct_safe("threeYearAverageReturn"))
                        f_item("5Y Return", fmt_pct_safe("fiveYearAverageReturn"))
                        f_item("Rating", info.get("morningStarOverallRating", "—"))
                        f_item("Type", info.get("legalType", "—"))
                        f_item("Currency", info.get("currency", "USD"))
                    else:
                        f_item("Market Cap", fmt_num_safe("marketCap", prefix=cur))
                        f_item("Enterprise Val", fmt_num_safe("enterpriseValue", prefix=cur))
                        f_item("Trailing P/E", fmt_ratio_safe("trailingPE"))
                        f_item("Forward P/E", fmt_ratio_safe("forwardPE"))
                        f_item("PEG Ratio", fmt_ratio_safe("pegRatio"))
                        f_item("Price/Sales", fmt_ratio_safe("priceToSalesTrailing12Months"))
                        f_item("Price/Book", fmt_ratio_safe("priceToBook"))
                        f_item("EV/Revenue", fmt_ratio_safe("enterpriseToRevenue"))
                        f_item("EV/EBITDA", fmt_ratio_safe("enterpriseToEbitda"))
                        f_item("EPS (TTM)", fmt_num_safe("trailingEps", prefix=cur))
                        f_item("EPS Est", fmt_num_safe("forwardEps", prefix=cur))
                        f_item("Target Price", fmt_num_safe("targetMeanPrice", prefix=cur), "text-blue-400")
                        f_item("Profit Margin", fmt_pct_safe("profitMargins"), "text-green-300")
                        f_item("Operating Margin", fmt_pct_safe("operatingMargins"))
                        f_item("Gross Margin", fmt_pct_safe("grossMargins"))
                        f_item("ROE", fmt_pct_safe("returnOnEquity"), "text-blue-300")
                        f_item("ROA", fmt_pct_safe("returnOnAssets"))
                        f_item("Analyst Rec.", info.get("recommendationKey", "—").upper().replace("_", " "), "text-yellow-400")
                        f_item("Total Cash", fmt_num_safe("totalCash", prefix=cur))
                        f_item("Total Debt", fmt_num_safe("totalDebt", prefix=cur))
                        f_item("Debt/Equity", fmt_ratio_safe("debtToEquity"))
                        f_item("Current Ratio", fmt_ratio_safe("currentRatio"))
                        f_item("Quick Ratio", fmt_ratio_safe("quickRatio"))
                        f_item("Div Yield", fmt_pct_safe("dividendYield"), "text-yellow-300")
                        f_item("Revenue", fmt_num_safe("totalRevenue", prefix=cur))
                        f_item("Rev Growth", fmt_pct_safe("revenueGrowth"))
                        f_item("EBITDA", fmt_num_safe("ebitda", prefix=cur))
                        f_item("Beta", fmt_ratio_safe("beta"))
                        f_item("Avg Vol", fmt_num_safe("averageVolume", suffix=""))
                        f_item("Short Ratio", fmt_ratio_safe("shortRatio"))

            # --- 7. Charts ---
            has_financials = not is_etf and not financials.empty
            has_ownership = False
            insider_pct, inst_pct, public_pct = 0.0, 0.0, 100.0
            if major_holders_df is not None:
                try:
                    mh = major_holders_df.copy()
                    mh.columns = ["Value", "Label"]
                    insider_row = mh[mh["Label"].str.contains("Insiders", case=False, na=False)]
                    inst_row = mh[mh["Label"].str.contains("Institutions", case=False, na=False)]
                    if not insider_row.empty: insider_pct = float(insider_row.iloc[0]["Value"].replace("%", ""))
                    if not inst_row.empty: inst_pct = float(inst_row.iloc[0]["Value"].replace("%", ""))
                    public_pct = max(0, 100.0 - insider_pct - inst_pct)
                    if insider_pct + inst_pct > 0: has_ownership = True
                except: pass

            if has_financials or has_ownership:
                ui.label("Financials & Ownership").classes("text-lg font-bold text-white mt-2")
                with ui.grid().classes("w-full grid-cols-1 md:grid-cols-2 gap-4"):
                    if has_financials:
                        with ui.card().classes("bg-slate-900 border border-slate-700 p-3"):
                            ui.label("Annual Revenue vs. Earnings").classes("text-xs font-bold text-slate-300 uppercase mb-2")
                            dates = financials.index.strftime('%Y')
                            rev = financials.get("Total Revenue", financials.get("TotalRevenue", []))
                            inc = financials.get("Net Income", financials.get("NetIncome", []))
                            f_fig = go.Figure()
                            f_fig.add_trace(go.Bar(x=dates, y=rev, name="Revenue", marker_color="#3b82f6"))
                            f_fig.add_trace(go.Bar(x=dates, y=inc, name="Earnings", marker_color="#22c55e"))
                            f_fig.update_layout(template="plotly_dark", barmode='group', height=280, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", margin=dict(l=20, r=20, t=10, b=20), legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
                            ui.plotly(f_fig).classes("w-full h-[280px]")
                    if has_ownership:
                        with ui.card().classes("bg-slate-900 border border-slate-700 p-3 flex flex-col items-center"):
                            ui.label("Ownership Structure").classes("text-xs font-bold text-slate-300 uppercase mb-2 self-start")
                            h_fig = go.Figure(data=[go.Pie(labels=["Insiders", "Institutions", "Public"], values=[insider_pct, inst_pct, public_pct], hole=.6, marker=dict(colors=["#f59e0b", "#3b82f6", "#94a3b8"]), textinfo='label+percent', hoverinfo='label+value+percent', textposition='outside')])
                            h_fig.update_layout(template="plotly_dark", height=280, showlegend=False, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", margin=dict(l=20, r=20, t=20, b=20), annotations=[dict(text='Holders', x=0.5, y=0.5, font_size=14, showarrow=False, font_color="white")])
                            ui.plotly(h_fig).classes("w-full h-[280px]")

            # --- 8. Analyst Gauge ---
            if not is_etf:
                with ui.card().classes("w-full bg-slate-900 border border-slate-700 p-4"):
                    ui.label("Analyst Price Target").classes("text-sm font-bold text-slate-300 uppercase mb-4")
                    target = info.get("targetMeanPrice")
                    current = last["close"]
                    if target:
                        upside = ((target - current) / current) * 100
                        up_color = "text-green-400" if upside > 0 else "text-red-400"
                        with ui.row().classes("w-full items-baseline gap-4"):
                            ui.label(f"{cur}{target:,.2f}").classes("text-4xl font-black text-white")
                            ui.label(f"{upside:+.2f}% Upside").classes(f"text-lg font-bold {up_color}")
                        low, high = info.get("targetLowPrice", current*0.8), info.get("targetHighPrice", current*1.2)
                        
                        ui.html(f'''
                            <div style="width:100%; height:10px; background:#334155; border-radius:5px; position:relative; margin-top:10px;">
                                <div style="position:absolute; left:0; top:0; height:100%; width:100%; background: linear-gradient(90deg, #ef4444 0%, #eab308 50%, #22c55e 100%); opacity:0.3; border-radius:5px;"></div>
                                <div style="position:absolute; left:{min(max((current-low)/(high-low)*100, 0), 100)}%; top:-5px; width:4px; height:20px; background:white; border-radius:2px; box-shadow: 0 0 5px white;"></div>
                            </div>
                            <div style="display:flex; justify-content:space-between; margin-top:5px; color:#94a3b8; font-size:10px;">
                                <span>Low: {low}</span> <span>▲ Current</span> <span>High: {high}</span>
                            </div>
                        ''', sanitize=False)
                    else:
                        ui.label("No Analyst Data").classes("text-slate-500 italic")

            # --- 9. Technicals ---
            ui.label("Technical Strength").classes("text-lg font-bold text-white mt-4")
            with ui.grid().classes("w-full grid-cols-1 md:grid-cols-2 gap-4"):
                with ui.card().classes("bg-slate-900 border border-green-900/50 p-3"):
                    with ui.row().classes("items-center gap-2 mb-1"):
                        ui.icon("thumb_up").classes("text-green-400 text-sm")
                        ui.label("Good Signs").classes("text-green-400 font-bold text-xs uppercase")
                    for p in pro_con["Pros"]: ui.label(f"• {p}").classes("text-slate-300 text-sm ml-2")
                with ui.card().classes("bg-slate-900 border border-red-900/50 p-3"):
                    with ui.row().classes("items-center gap-2 mb-1"):
                        ui.icon("thumb_down").classes("text-red-400 text-sm")
                        ui.label("Bad Signs").classes("text-red-400 font-bold text-xs uppercase")
                    for c in pro_con["Cons"]: ui.label(f"• {c}").classes("text-slate-300 text-sm ml-2")

            ui.label("Price Chart").classes("text-lg font-bold text-white mt-4")
            fig = go.Figure()
            fig.add_trace(go.Candlestick(x=df['date'], open=df['open'], high=df['high'], low=df['low'], close=df['close'], name="Price"))
            fig.add_trace(go.Scatter(x=df['date'], y=df['ma20'], line=dict(color='#2962FF', width=1), name='MA20'))
            fig.add_trace(go.Scatter(x=df['date'], y=df['ma50'], line=dict(color='#FF6D00', width=1), name='MA50'))
            fig.add_trace(go.Scatter(x=df['date'], y=df['ma200'], line=dict(color='#EEEEEE', width=1), name='MA200'))
            if pd.notna(sig['Stop']): fig.add_hline(y=sig['Stop'], line_dash="dash", line_color="red", annotation_text="Stop")
            if pd.notna(sig['Target']): fig.add_hline(y=sig['Target'], line_dash="dash", line_color="green", annotation_text="Target")
            fig.update_layout(template="plotly_dark", height=500, margin=dict(l=40,r=40,t=30,b=30), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", xaxis_rangeslider_visible=False)
            ui.plotly(fig).classes("w-full h-[500px] bg-slate-900 rounded-xl border border-slate-700")

            # --- 10. Peers & Patterns ---
            with ui.grid().classes("w-full grid-cols-1 md:grid-cols-2 gap-4 mt-4"):
                with ui.column().classes("gap-2"):
                    ui.label(f"Peer Comparison ({sector})").classes("text-lg font-bold text-white")
                    peers = get_peers(ticker)
                    if peers:
                        peer_rows = []
                        for p in peers:
                            p_df = fetch_yf(p['ticker'], start, end)
                            if not p_df.empty:
                                p_df = add_indicators(p_df)
                                p_last = p_df.iloc[-1]
                                p_sig = get_decision(p_df)
                                p_market = p.get('market', 'USA')
                                p_cur = "₹" if p_market == 'INDIA' else "$"
                                peer_rows.append({"Ticker": p['ticker'], "Name": p['name'], "Price": f"{p_cur}{p_last['close']:.2f}", "Score": int(p_sig['Score']), "Decision": p_sig['Decision']})
                        
                        if peer_rows:
                            p_cols = [
                                {'name': 'Ticker', 'label': 'Ticker', 'field': 'Ticker', 'align': 'left'},
                                {'name': 'Name', 'label': 'Company', 'field': 'Name', 'align': 'left'},
                                {'name': 'Price', 'label': 'Price', 'field': 'Price', 'align': 'right'},
                                {'name': 'Score', 'label': 'Score', 'field': 'Score', 'align': 'center'},
                                {'name': 'Decision', 'label': 'Action', 'field': 'Decision', 'align': 'center'},
                            ]
                            p_table = ui.table(columns=p_cols, rows=peer_rows).classes("w-full border-slate-700")
                            p_table.props("dark flat dense")
                            p_table.add_slot('body-cell-Ticker', '''<q-td :props="props"><a :href="'/detail/'+props.value" class="text-blue-400 font-bold no-underline">{{props.value}}</a></q-td>''')
                            p_table.add_slot('body-cell-Decision', '''<q-td :props="props"><q-badge :color="props.value==='BUY'?'green':(props.value==='AVOID'?'red':'orange')" outline>{{props.value}}</q-badge></q-td>''')
                    else:
                        ui.label("No peers found.").classes("text-slate-500 italic")

                with ui.column().classes("gap-2"):
                    ui.label("Candle Patterns (Last 5 Days)").classes("text-lg font-bold text-white")
                    patterns = detect_patterns(df, n_days=5)
                    if patterns:
                        with ui.column().classes("w-full gap-2"):
                            for p in patterns:
                                dstr = p['Date'].strftime('%Y-%m-%d')
                                with ui.row().classes("items-center gap-2 bg-slate-900 border border-slate-700 p-2 w-full"):
                                    ui.icon("candlestick_chart").classes("text-yellow-500 text-lg")
                                    ui.label(f"{dstr}").classes("text-slate-400 font-mono text-sm")
                                    ui.label(p['Pattern']).classes("text-white font-bold text-md")
                                    ui.label(f"— {p['Meaning']}").classes("text-slate-300 italic text-sm")
                                    if p.get('Learn'): 
                                        ui.link("Learn ↗", p['Learn'], new_tab=True).classes("text-blue-400 ml-auto text-sm no-underline hover:text-blue-300")
                    else:
                        ui.label("No patterns detected.").classes("text-slate-500 italic")

            ui.label("Manual Risk Plan").classes("text-xl font-bold text-white mt-6")
            with ui.grid().classes("w-full grid-cols-2 md:grid-cols-4 gap-4"):
                def stat_card(label, value, color="text-white"):
                    with ui.card().classes("bg-slate-900 border border-slate-700 p-4"):
                        ui.label(label).classes("text-slate-400 text-xs uppercase font-bold")
                        ui.label(str(value)).classes(f"text-2xl font-bold {color}")
                stat_card("ATR (Volatility)", f"{sig['ATR']:.2f}")
                stat_card("Stop Price", f"${sig['Stop']:.2f}" if pd.notna(sig['Stop']) else "N/A", "text-red-500")
                stat_card("Target Price", f"${sig['Target']:.2f}" if pd.notna(sig['Target']) else "N/A", "text-green-500")
                stat_card("RSI", f"{sig['RSI']:.0f}", "text-yellow-400")