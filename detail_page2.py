from nicegui import ui
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
import datetime as dt
from logic import fetch_yf, add_indicators, get_decision, get_peers, detect_patterns 
from logic2 import get_quant_dna, run_monte_carlo, calculate_roce, get_performance_stats
from universe import COMPANIES # Need access to full list for fallback

# --- 1. INTERACTIVE CHART COMPONENT ---
def render_interactive_section(full_df, market_currency):
    ui.label("Interactive Charts (Select TIme)").classes("text-lg font-bold text-white mt-6")
    chart_state = {'days': 365} 
    @ui.refreshable
    def _render_chart():
        days = chart_state['days']
        cutoff = full_df.iloc[-1]['date'] - dt.timedelta(days=days)
        df_slice = full_df[full_df['date'] > cutoff].copy()
        if df_slice.empty: return
        first, last = df_slice.iloc[0], df_slice.iloc[-1]
        period_return = ((last['close'] - first['close']) / first['close']) * 100
        period_high, period_low = df_slice['high'].max(), df_slice['low'].min()
        period_vol = df_slice['close'].pct_change().std() * np.sqrt(252) * 100
        with ui.grid().classes("grid-cols-4 w-full gap-4 mb-4"):
            def s_card(label, val, col):
                with ui.card().classes("bg-slate-800 border border-slate-700 p-3"):
                    ui.label(label).classes("text-[10px] text-slate-400 uppercase font-bold"); ui.label(val).classes(f"text-xl font-bold {col}")
            s_card("Period Return", f"{period_return:+.2f}%", "text-green-400" if period_return>0 else "text-red-400")
            s_card("Period High", f"{market_currency}{period_high:.2f}", "text-white")
            s_card("Period Low", f"{market_currency}{period_low:.2f}", "text-white")
            s_card("Volatility (Ann.)", f"{period_vol:.1f}%", "text-yellow-400")
        
        fig = make_subplots(rows=3, cols=1, shared_xaxes=True, row_heights=[0.6, 0.2, 0.2], subplot_titles=("Price Action", "Volume", "MACD Momentum"))
        fig.add_trace(go.Candlestick(x=df_slice['date'], open=df_slice['open'], high=df_slice['high'], low=df_slice['low'], close=df_slice['close'], name="Price"), row=1, col=1)
        fig.add_trace(go.Scatter(x=df_slice['date'], y=df_slice['ma20'], line=dict(color='#2962FF', width=1), name='MA20'), row=1, col=1)
        fig.add_trace(go.Scatter(x=df_slice['date'], y=df_slice['ma50'], line=dict(color='#FF6D00', width=1), name='MA50'), row=1, col=1)
        if 'bb_upper' in df_slice.columns:
            fig.add_trace(go.Scatter(x=df_slice['date'], y=df_slice['bb_upper'], line=dict(color='rgba(255, 255, 255, 0.3)', width=1, dash='dot'), showlegend=False), row=1, col=1)
            fig.add_trace(go.Scatter(x=df_slice['date'], y=df_slice['bb_lower'], line=dict(color='rgba(255, 255, 255, 0.3)', width=1, dash='dot'), showlegend=False), row=1, col=1)
        colors = ['#ef4444' if row['open'] > row['close'] else '#22c55e' for index, row in df_slice.iterrows()]
        fig.add_trace(go.Bar(x=df_slice['date'], y=df_slice['volume'], marker_color=colors, name="Volume"), row=2, col=1)
        if 'macd' in df_slice.columns:
            fig.add_trace(go.Scatter(x=df_slice['date'], y=df_slice['macd'], line=dict(color='#2962FF', width=1.5), name='MACD'), row=3, col=1)
            fig.add_trace(go.Scatter(x=df_slice['date'], y=df_slice['signal'], line=dict(color='#FF6D00', width=1.5), name='Signal'), row=3, col=1)
            fig.add_trace(go.Bar(x=df_slice['date'], y=df_slice['hist'], marker_color='#9ca3af', name='Hist'), row=3, col=1)
        
        fig.update_layout(template="plotly_dark", height=800, xaxis_rangeslider_visible=False, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", margin=dict(l=60,r=40,t=30,b=30), yaxis=dict(title="Price", tickprefix=market_currency), yaxis2=dict(title="Volume"), yaxis3=dict(title="Oscillator"))
        ui.plotly(fig).classes("w-full h-[800px] bg-slate-900 rounded-xl border border-slate-700")
        
    with ui.row().classes("w-full gap-2 mb-4"):
        def set_tf(d): chart_state['days'] = d; _render_chart.refresh()
        for label, d in [("1W", 7), ("1M", 30), ("3M", 90), ("6M", 180), ("1Y", 365), ("3Y", 1095), ("5Y", 1825)]:
            ui.button(label, on_click=lambda d=d: set_tf(d)).props("outline dense size=sm")
    _render_chart()

def render_quant_dna_section(ticker, info, df):
    ui.label("Quant DNA (PhD Advisor)").classes("text-xl font-bold text-white mt-6")
    quant_dna = get_quant_dna(ticker, info, df)
    with ui.grid().classes("w-full grid-cols-1 md:grid-cols-3 gap-6"):
        with ui.card().classes("bg-slate-900 border border-slate-700 p-4 col-span-1 h-[400px]"):
            if quant_dna:
                categories = list(quant_dna.keys()); values = list(quant_dna.values())
                categories.append(categories[0]); values.append(values[0])
                fig_dna = go.Figure()
                fig_dna.add_trace(go.Scatterpolar(r=values, theta=categories, fill='toself', name=ticker, line=dict(color='#8b5cf6', width=2), fillcolor='rgba(139, 92, 246, 0.2)'))
                fig_dna.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 100], showticklabels=False, linecolor='#334155'), bgcolor='rgba(0,0,0,0)'), showlegend=False, template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", margin=dict(l=80, r=80, t=20, b=20))
                ui.plotly(fig_dna).classes("w-full h-full")
            else: ui.label("Not enough data.").classes("text-slate-500 italic self-center")
        with ui.column().classes("col-span-1 md:col-span-2 gap-4"):
            def dna_row(label, score, desc, tooltip):
                col = "text-green-400" if score >= 70 else ("text-yellow-400" if score >= 40 else "text-red-400")
                with ui.card().classes("bg-slate-800 border border-slate-700 p-3 w-full flex-row justify-between items-center"):
                    with ui.row().classes("items-center gap-2"):
                        ui.label(label).classes("text-sm font-bold text-white uppercase w-24")
                        ui.icon("info").classes("text-slate-500 text-xs cursor-help").tooltip(tooltip)
                    with ui.row().classes("items-center gap-4"):
                        ui.label(desc).classes("text-xs text-slate-400 italic hidden sm:block")
                        ui.label(f"{score}/100").classes(f"text-xl font-black font-mono {col}")
            dna_row("Value", quant_dna.get("Value", 0), "Is it cheap?", "Based on P/E Ratio.")
            dna_row("Momentum", quant_dna.get("Momentum", 0), "Is it trending?", "Based on RSI & Price vs MA.")
            dna_row("Quality", quant_dna.get("Quality", 0), "Is it profitable?", "Based on Margins & ROE.")
            dna_row("Stability", quant_dna.get("Stability", 0), "Is it safe?", "Based on Beta (Volatility).")

# --- 3. FUNDAMENTALS GRID ---
def render_fundamentals_section(ticker, info, is_etf, cur):
    ui.label(f"Fundamentals ({'ETF Protocol' if is_etf else 'Stock Protocol'})").classes("text-lg font-bold text-white mt-2")
    roce_data = calculate_roce(ticker)
    
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
        return f"{val*100:.2f}%" if val and isinstance(val, (int, float)) else "—"
    def fmt_ratio_safe(key):
        val = info.get(key)
        return f"{val:.2f}" if val and isinstance(val, (int, float)) else "—"

    with ui.card().classes("w-full bg-slate-900 border border-slate-700 p-0"):
        with ui.grid().classes("grid-cols-2 sm:grid-cols-3 md:grid-cols-6 w-full gap-px bg-slate-700"):
            def f_item(label, value, color="text-white"):
                with ui.column().classes("bg-slate-900 p-2 justify-center h-full"):
                    ui.label(label).classes("text-[9px] uppercase font-bold text-slate-400 tracking-wider truncate w-full")
                    ui.label(str(value)).classes(f"text-xs md:text-sm font-bold {color} truncate w-full")
            
            if not is_etf:
                f_item("ROCE (TTM)", roce_data['current'], "text-purple-400")
                f_item("ROCE (3Y Avg)", roce_data['avg3y'], "text-purple-300")
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
                f_item("Payout Ratio", fmt_pct_safe("payoutRatio"))
                f_item("Book Value", fmt_num_safe("bookValue", prefix=cur))
                f_item("Free Cash Flow", fmt_num_safe("freeCashflow", prefix=cur))
                f_item("52W High", fmt_num_safe("fiftyTwoWeekHigh", prefix=cur))
                f_item("52W Low", fmt_num_safe("fiftyTwoWeekLow", prefix=cur))
                f_item("Employees", f"{info.get('fullTimeEmployees', 0):,}")
            else:
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

def render_performance_table(df):
    ui.label("Trailing Returns (CAGR)").classes("text-xl font-bold text-white mt-6")
    perf_stats = get_performance_stats(df)
    with ui.card().classes("w-full bg-slate-900 border border-slate-700 p-0"):
        with ui.grid().classes("grid-cols-5 w-full divide-x divide-slate-700"):
            def perf_box(period, val):
                with ui.column().classes("items-center p-3"):
                    ui.label(period).classes("text-xs font-bold text-slate-500 uppercase")
                    if isinstance(val, (int, float)):
                        col = "text-green-400" if val >= 0 else "text-red-400"
                        ui.label(f"{val:+.2f}%").classes(f"text-lg font-black {col}")
                    else: ui.label(str(val)).classes("text-lg font-bold text-slate-500")
            perf_box("1 Week", perf_stats.get("1W"))
            perf_box("1 Month", perf_stats.get("1M"))
            perf_box("1 Year", perf_stats.get("1Y"))
            perf_box("3 Years", perf_stats.get("3Y"))
            perf_box("5 Years", perf_stats.get("5Y"))

def render_financials_ownership(financials, major_holders, is_etf):
    has_financials = not is_etf and not financials.empty
    has_ownership = False
    insider_pct, inst_pct, public_pct = 0.0, 0.0, 100.0
    if major_holders is not None:
        try:
            mh = major_holders.copy()
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

# --- 6. PEERS & PATTERNS (FIXED MARKET & SECTOR LOGIC) ---
def render_peers_patterns(ticker, sector, df, start_date, end_date, market):
    # Fallback to local peers if get_peers() returns nothing
    # This logic finds companies in the same sector OR with the same market
    my_company = next((c for c in COMPANIES if c['ticker'] == ticker), None)
    
    # Logic: Get peers that share Sector AND (Market OR Currency)
    # This fixes ICICI (NSE) not matching other Banks (NSE) if market strings differed slightly
    peers = []
    if my_company:
        sector_match = my_company.get('sector')
        market_match = my_company.get('market')
        for c in COMPANIES:
            if c['ticker'] == ticker: continue
            if c.get('sector') == sector_match and (c.get('market') == market_match):
                peers.append(c)
    
    # Limit to 5 peers
    peers = peers[:5]

    with ui.grid().classes("w-full grid-cols-1 md:grid-cols-2 gap-4 mt-4"):
        with ui.column().classes("gap-2"):
            ui.label(f"Peer Comparison ({sector})").classes("text-lg font-bold text-white")
            
            if peers:
                peer_rows = []
                for p in peers:
                    p_df = fetch_yf(p['ticker'], start_date, end_date)
                    if not p_df.empty:
                        p_df = add_indicators(p_df); p_sig = get_decision(p_df)
                        p_cur = "₹" if p.get('market') == 'INDIA' else "$"
                        peer_rows.append({"Ticker": p['ticker'], "Name": p['name'], "Price": f"{p_cur}{p_df.iloc[-1]['close']:.2f}", "Score": int(p_sig['Score']), "Decision": p_sig['Decision']})
                if peer_rows:
                    p_table = ui.table(columns=[{'name':'Ticker','label':'Ticker','field':'Ticker'}, {'name':'Name','label':'Name','field':'Name'}, {'name':'Price','label':'Price','field':'Price'}, {'name':'Score','label':'Score','field':'Score'}, {'name':'Decision','label':'Action','field':'Decision'}], rows=peer_rows).classes("w-full border-slate-700")
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

def render_monte_carlo_section(df, cur):
    ui.label("Future Simulator (Monte Carlo)").classes("text-xl font-bold text-white mt-6")
    monte_carlo = run_monte_carlo(df)
    with ui.card().classes("w-full bg-slate-900 border border-slate-700 p-4"):
        if monte_carlo:
            p95, p50, p05 = monte_carlo['p95'], monte_carlo['p50'], monte_carlo['p05']
            days = list(range(len(p95)))
            fig_mc = go.Figure()
            fig_mc.add_trace(go.Scatter(x=days, y=p95, name='Bull (95%)', line=dict(color='#22c55e', dash='dot')))
            fig_mc.add_trace(go.Scatter(x=days, y=p50, name='Median', line=dict(color='#3b82f6', width=3)))
            fig_mc.add_trace(go.Scatter(x=days, y=p05, name='Bear (5%)', line=dict(color='#ef4444', dash='dot'), fill='tonexty'))
            fig_mc.update_layout(template="plotly_dark", height=400, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", xaxis_title="Days", yaxis=dict(title="Price", tickprefix=cur))
            ui.plotly(fig_mc).classes("w-full h-[400px]")
            with ui.row().classes("w-full justify-between mt-2 px-2"):
                ui.label(f"Bear: {cur}{p05[-1]:.2f}").classes("text-red-400 font-mono font-bold")
                ui.label(f"Median: {cur}{p50[-1]:.2f}").classes("text-blue-400 font-mono font-bold")
                ui.label(f"Bull: {cur}{p95[-1]:.2f}").classes("text-green-400 font-mono font-bold")
            with ui.expansion("How to Read", icon="help_outline").classes("w-full bg-slate-800/50 mt-2 text-slate-300"):
                ui.markdown("* **Green (Bull):** Top 5% best-case scenario.\n* **Blue (Median):** Most likely path.\n* **Red (Bear):** Worst 5% crash scenario.")
        else:
            ui.label("Not enough history.").classes("text-slate-500")