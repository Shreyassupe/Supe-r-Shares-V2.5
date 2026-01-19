from nicegui import ui
import portfolio_manager as pm
from theme import frame
from logic import score_portfolio
from logic2 import get_portfolio_correlation
from universe import COMPANIES
import pandas as pd
import plotly.graph_objects as go
import numpy as np

def render_portfolio():
    with frame(title="My Portfolio"):
        
        # --- 1. SELL DIALOG ---
        def open_sell_dialog(ticker, current_qty, current_price):
            # Safe float conversion
            try: current_price = float(current_price)
            except: current_price = 0.0
            
            with ui.dialog() as dialog, ui.card().classes("bg-slate-900 border border-slate-700 w-96"):
                ui.label(f"Close Position: {ticker}").classes("text-xl font-bold text-white mb-4")
                qty_input = ui.number(label="Shares to Sell", value=current_qty, min=0.01, max=current_qty).classes("w-full mb-2")
                price_input = ui.number(label="Sell Price", value=current_price, format="%.2f").classes("w-full mb-6")
                
                def confirm_sell():
                    success = pm.sell_stock(ticker, qty_input.value, price_input.value)
                    if success:
                        ui.notify(f"Sold {qty_input.value} {ticker}", color="green")
                        dialog.close()
                        ui.navigate.reload()
                    else:
                        ui.notify("Error: Invalid Quantity", color="red")

                with ui.row().classes("w-full justify-end"):
                    ui.button("Cancel", on_click=dialog.close).props("flat color=grey")
                    ui.button("CONFIRM SALE", on_click=confirm_sell).props("color=green")
            dialog.open()

        # --- CONTAINER (Gap Fix: pt-0 mt-0) ---
        with ui.column().classes("w-full max-w-7xl mx-auto px-4 pb-4 pt-0 mt-0 gap-6"):
            
            # --- 2. DATA MERGING (The Fix for Disappearing Stocks) ---
            active_holdings = pm.get_active_holdings() # Raw list from JSON
            
            if active_holdings:
                # 1. Create a Base DataFrame from JSON (Guarantees rows exist)
                df_raw = pd.DataFrame(active_holdings)
                df_raw['ticker'] = df_raw['ticker'].astype(str)
                
                # 2. Try to fetch scores/prices
                try:
                    df_scores = score_portfolio(active_holdings)
                except:
                    df_scores = pd.DataFrame() # Fallback if API fails completely

                # 3. Merge safely
                if not df_scores.empty:
                    # Rename columns to match if needed, but assuming score_portfolio returns 'Ticker'
                    # We map the scored data onto the raw data
                    df_scores['Ticker'] = df_scores['Ticker'].astype(str)
                    df = pd.merge(df_raw, df_scores, left_on='ticker', right_on='Ticker', how='left')
                    
                    # Fill NaN for stocks that failed to download
                    df['CurrentVal'] = df['CurrentVal'].fillna(df['avg_price'] * df['qty']) # Fallback to cost basis
                    df['CurrentPrice'] = df['CurrentPrice'].fillna(df['avg_price'])
                    df['P&L'] = df['P&L'].fillna(0)
                    df['P&L%'] = df['P&L%'].fillna(0)
                    df['DailyP&L'] = df['DailyP&L'].fillna(0)
                    df['DailyChg%'] = df['DailyChg%'].fillna(0)
                    df['Decision'] = df['Decision'].fillna("WAIT")
                    df['Reason'] = df['Reason'].fillna("Data Unavailable")
                    df['Company'] = df['Company'].fillna(df['ticker'])
                    df['Sector'] = df['Sector'].fillna("Other")
                else:
                    # Total API Failure Fallback
                    df = df_raw.copy()
                    df['Ticker'] = df['ticker']
                    df['Qty'] = df['qty']
                    df['AvgPrice'] = df['avg_price']
                    df['CurrentPrice'] = df['avg_price']
                    df['CurrentVal'] = df['qty'] * df['avg_price']
                    df['P&L'] = 0.0
                    df['P&L%'] = 0.0
                    df['DailyP&L'] = 0.0
                    df['DailyChg%'] = 0.0
                    df['Decision'] = "WAIT"
                    df['Reason'] = "Connection Failed"
                    df['Company'] = df['ticker']
                    df['Sector'] = "Other"

                # Calc Totals
                current_value = df["CurrentVal"].sum()
                total_invested = (df['qty'] * df['avg_price']).sum()
                total_pl = current_value - total_invested
                total_pl_pct = (total_pl / total_invested * 100) if total_invested > 0 else 0
                day_pl_sum = df["DailyP&L"].sum()
                
                pl_color = "text-green-400" if total_pl >= 0 else "text-red-400"
                day_color = "text-green-400" if day_pl_sum >= 0 else "text-red-400"
            else:
                df = pd.DataFrame()
                current_value, total_pl, total_pl_pct, day_pl_sum = 0,0,0,0
                pl_color, day_color = "text-slate-400", "text-slate-400"

            # Header
            with ui.row().classes("w-full justify-between items-end border-b border-slate-800 pb-4 mt-6"):
                with ui.column().classes("gap-1"):
                    ui.label("My Portfolio").classes("text-3xl font-black text-white")
                    if active_holdings:
                        with ui.row().classes("items-center gap-2"):
                            ui.label("Today's P&L:").classes("text-sm font-bold text-slate-400")
                            ui.label(f"${day_pl_sum:+,.2f}").classes(f"text-sm font-black {day_color}")

                with ui.column().classes("items-end gap-0"):
                    ui.label("Total Net Worth").classes("text-xs font-bold text-slate-400 uppercase")
                    ui.label(f"${current_value:,.2f}").classes(f"text-3xl font-black {pl_color}")
                    ui.label(f"{total_pl:+,.2f} ({total_pl_pct:+.2f}%)").classes(f"text-sm font-mono font-bold {pl_color}")

            # --- 3. TABS ---
            with ui.tabs().classes('w-full text-white bg-slate-800 rounded-t-lg') as tabs:
                active_tab = ui.tab('Active Holdings').props('icon=pie_chart') 
                risk_tab = ui.tab('Risk Analysis').props('icon=shield') 
                history_tab = ui.tab('All-Time History').props('icon=history')

            # --- 4. PANELS ---
            with ui.tab_panels(tabs, value=active_tab).classes('w-full bg-transparent p-0'):
                with ui.tab_panel(active_tab).classes('p-0'):
                    if df.empty:
                        ui.label("No active holdings.").classes("text-slate-500 italic mt-4")
                    else:
                        render_active_view(df, open_sell_dialog)

                with ui.tab_panel(risk_tab).classes('p-0'):
                    if not active_holdings:
                        ui.label("No active holdings to analyze.").classes("text-slate-500 italic mt-4")
                    else:
                        render_risk_view(active_holdings)

                with ui.tab_panel(history_tab).classes('p-0'):
                    history_data = pm.get_trade_history()
                    if not history_data:
                        ui.label("No transaction history yet.").classes("text-slate-500 italic mt-4")
                    else:
                        render_history_view(history_data)

def render_active_view(df, sell_callback):
    # 1. Charts
    with ui.grid().classes("w-full grid-cols-1 md:grid-cols-2 gap-4 my-4"):
        # Safe chart generation even with missing data
        df_sorted = df.sort_values(by="CurrentVal", ascending=False)
        tickers = df_sorted['Ticker'].tolist()
        chart_data = [{'value': row['CurrentVal'], 'itemStyle': {'color': '#3b82f6'}, 'name': row['Ticker']} for _, row in df_sorted.iterrows()]
        
        with ui.card().classes('bg-gray-900 border border-gray-700 p-4 h-80'):
            ui.label('Allocation by Ticker').classes('text-xs font-bold text-gray-400 uppercase mb-2')
            ui.echart({
                'tooltip': {'trigger': 'axis'},
                'grid': {'left': '3%', 'right': '4%', 'bottom': '3%', 'containLabel': True},
                'xAxis': [{'type': 'category', 'data': tickers, 'axisLabel': {'color': '#9ca3af'}}],
                'yAxis': [{'type': 'value', 'axisLabel': {'color': '#9ca3af'}, 'splitLine': {'lineStyle': {'color': '#374151'}}}],
                'series': [{'name': 'Value', 'type': 'bar', 'data': chart_data, 'barWidth': '50%'}]
            }).classes('w-full h-full')

        sector_data = df.groupby("Sector")["CurrentVal"].sum().reset_index()
        pie_data = [{"value": row["CurrentVal"], "name": row["Sector"]} for _, row in sector_data.iterrows()]
        with ui.card().classes('bg-gray-900 border border-gray-700 p-4 h-80'):
            ui.label('Sector Exposure').classes('text-xs font-bold text-gray-400 uppercase mb-2')
            ui.echart({
                'tooltip': {'trigger': 'item'},
                'legend': {'top': '5%', 'left': 'center', 'textStyle': {'color': '#ccc'}},
                'series': [{
                    'name': 'Sector', 'type': 'pie', 'radius': ['40%', '70%'],
                    'avoidLabelOverlap': False,
                    'itemStyle': {'borderRadius': 5, 'borderColor': '#111827', 'borderWidth': 2},
                    'label': {'show': False},
                    'data': pie_data
                }]
            }).classes('w-full h-full')

    # 2. Table
    records = df.to_dict("records")
    for row in records:
        # Safe formatting with fallback to 0
        ap = float(row.get('avg_price', 0) or 0)
        cp = float(row.get('CurrentPrice', 0) or 0)
        cv = float(row.get('CurrentVal', 0) or 0)
        pl = float(row.get('P&L', 0) or 0)
        pl_pct = float(row.get('P&L%', 0) or 0)
        d_pl = float(row.get('DailyP&L', 0) or 0)
        d_pct = float(row.get('DailyChg%', 0) or 0)

        row['AvgPrice_Str'] = f"${ap:,.2f}"
        row['CurrentPrice_Str'] = f"${cp:,.2f}"
        row['CurrentVal_Str'] = f"${cv:,.2f}"
        row['P&L_Str'] = f"{pl:+,.2f} ({pl_pct:+.2f}%)"
        row['Daily_Str'] = f"{d_pl:+,.2f} ({d_pct:+.2f}%)"
        row['Decision'] = row.get('Decision', 'WAIT')

    cols = [
        {'name':'Action', 'label':'', 'field':'Ticker', 'align':'center'}, 
        {'name':'Ticker', 'label':'TICKER', 'field':'Ticker', 'sortable':True, 'align':'left'},
        {'name':'Company', 'label':'COMPANY', 'field':'Company', 'sortable':True, 'align':'left'},
        {'name':'Sector', 'label':'SECTOR', 'field':'Sector', 'sortable':True, 'align':'left'}, 
        {'name':'Qty', 'label':'QTY', 'field':'qty', 'sortable':True, 'align':'center'},
        {'name':'AvgPrice', 'label':'AVG', 'field':'AvgPrice_Str', 'align':'right'},
        {'name':'CurrentPrice', 'label':'PRICE', 'field':'CurrentPrice_Str', 'align':'right'},
        {'name':'CurrentVal', 'label':'VALUE', 'field':'CurrentVal_Str', 'align':'right', 'sortable':True},
        {'name':'Daily_Str', 'label':'TODAY', 'field':'Daily_Str', 'align':'right', 'sortable':True}, 
        {'name':'P&L_Str', 'label':'TOTAL P&L', 'field':'P&L_Str', 'align':'right', 'sortable':True},
        {'name':'Decision', 'label':'ADVICE', 'field':'Decision', 'sortable':True, 'align':'center'},
    ]
    
    table = ui.table(columns=cols, rows=records, row_key='Ticker').classes('w-full border-slate-700')
    table.props("dark flat dense")
    
    table.add_slot('body-cell-Daily_Str', r'''<q-td :props="props" :class="props.value.includes('+')?'text-green-400 font-mono font-bold':(props.value.includes('-')?'text-red-400 font-mono font-bold':'text-slate-500')">{{props.value}}</q-td>''')
    table.add_slot('body-cell-P&L_Str', r'''<q-td :props="props" :class="props.value.includes('+')?'text-green-400 font-mono font-bold':'text-red-400 font-mono font-bold'">{{props.value}}</q-td>''')
    
    # --- CORRECT COLOR LOGIC ---
    # SWING=Cyan, BUY/INVEST=Green, WATCH=Blue, WAIT=Orange, AVOID=Red
    table.add_slot('body-cell-Decision', r'''
        <q-td :props="props">
            <div class="relative inline-block">
                <q-badge :color="props.value.includes('SWING') ? 'cyan' : (props.value.includes('WATCH') ? 'blue' : (props.value.includes('WAIT') ? 'orange' : (props.value.includes('BUY') || props.value.includes('INVEST') ? 'green' : 'red')))" 
                         class="font-bold text-xs p-2 cursor-help pr-3 text-black" :class="props.value.includes('SWING') ? 'text-black' : 'text-white'">
                    {{props.value}}
                    <q-tooltip anchor="top middle" self="bottom middle" :offset="[10, 10]" class="bg-slate-800 text-white shadow-lg border border-slate-600 text-sm p-2">
                        {{ props.row.Reason }}
                    </q-tooltip>
                </q-badge>
                <div class="absolute top-0 right-0 -mt-1 -mr-1 bg-white text-slate-900 rounded-full w-3 h-3 flex items-center justify-center text-[8px] font-bold pointer-events-none shadow-sm">i</div>
            </div>
        </q-td>
    ''')
    table.add_slot('body-cell-Ticker', r'''<q-td :props="props"><a :href="'/detail/'+props.value" class="text-blue-400 font-bold no-underline">{{props.value}}</a></q-td>''')
    
    table.add_slot('body-cell-Action', r'''
        <q-td :props="props">
            <div class="flex gap-2 justify-center">
                <q-btn flat dense round icon="monetization_on" color="green" size="sm" @click.stop="$parent.$emit('sell', props.row)"><q-tooltip>Close Position</q-tooltip></q-btn>
                <q-btn flat dense round icon="delete" color="red" size="sm" @click.stop="$parent.$emit('del', props.row)"><q-tooltip>Delete Record</q-tooltip></q-btn>
            </div>
        </q-td>
    ''')
    table.on('del', lambda e: (pm.remove_from_portfolio(e.args['Ticker']), ui.navigate.reload()))
    table.on('sell', lambda e: sell_callback(e.args['Ticker'], e.args['qty'], e.args['CurrentPrice']))

def render_risk_view(active_holdings):
    tickers = [item['ticker'] for item in active_holdings]
    if len(tickers) < 2:
        ui.label("Need at least 2 stocks for correlation analysis.").classes("text-slate-500 italic mt-4")
        return

    res = get_portfolio_correlation(tickers)
    matrix = res['matrix']
    score = res['diversity_score']

    with ui.card().classes("w-full bg-gradient-to-r from-slate-900 to-slate-800 border border-slate-700 p-6 mb-4"):
        with ui.row().classes("items-center gap-8"):
            with ui.column().classes("items-center relative justify-center w-[80px] h-[80px]"):
                color = "green" if score >= 70 else ("orange" if score >= 40 else "red")
                ui.circular_progress(score/100, show_value=False, size="90px", color=color).props("thickness=0.2 track-color=grey-8")
                ui.label(f"{score}/100").classes(f"absolute text-xl font-black text-{color}-400")
            
            with ui.column().classes("gap-1"):
                ui.label("Portfolio Diversity Score").classes("text-lg font-bold text-white uppercase tracking-wide")
                desc = "Excellent! Stocks are uncorrelated." if score >= 70 else ("Moderate overlap." if score >= 40 else "Danger! High Concentration Risk.")
                ui.label(desc).classes("text-slate-400 italic text-sm")

    ui.label("Correlation Matrix (1yr Daily Returns)").classes("text-xl font-bold text-white mb-4")
    
    if not matrix.empty:
        z_vals = matrix.values.tolist()
        x_lbl = matrix.columns.tolist()
        y_lbl = matrix.index.tolist()
        
        fig = go.Figure(data=go.Heatmap(
            z=z_vals, x=x_lbl, y=y_lbl,
            colorscale=[[0, '#3b82f6'], [0.5, '#1e293b'], [1, '#ef4444']], 
            zmin=-1, zmax=1,
            text=np.round(z_vals, 2), texttemplate="%{text}",
            showscale=True
        ))
        fig.update_layout(
            template="plotly_dark", height=800, 
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=50, r=50, t=20, b=50),
            xaxis=dict(side="bottom")
        )
        ui.plotly(fig).classes("w-full h-[800px] bg-slate-900 border border-slate-700 rounded-xl")

def render_history_view(history_list):
    processed = []
    for item in history_list:
        buy = float(item.get("buy_price", 0))
        sell = float(item.get("sell_price", 0))
        profit = float(item.get("profit", 0))
        invested = buy * item.get("qty_sold", 0)
        ret_pct = (profit / invested * 100) if invested > 0 else 0
        processed.append({
            "Date": item.get("date", "—"),
            "Ticker": item.get("ticker"),
            "Qty": item.get("qty_sold", 0),
            "BuyPrice": f"${buy:,.2f}",
            "SellPrice": f"${sell:,.2f}" if sell > 0 else "Legacy",
            "Profit": f"${profit:+,.2f}",
            "Return": f"{ret_pct:+.2f}%"
        })
    processed.sort(key=lambda x: x["Date"], reverse=True)

    cols = [
        {'name':'Date', 'label':'DATE', 'field':'Date', 'align':'left', 'sortable':True},
        {'name':'Ticker', 'label':'TICKER', 'field':'Ticker', 'align':'left', 'sortable':True},
        {'name':'Qty', 'label':'QTY SOLD', 'field':'Qty', 'align':'center'},
        {'name':'BuyPrice', 'label':'BUY PRICE', 'field':'BuyPrice', 'align':'right'},
        {'name':'SellPrice', 'label':'SELL PRICE', 'field':'SellPrice', 'align':'right'},
        {'name':'Profit', 'label':'REALIZED P&L', 'field':'Profit', 'align':'right', 'sortable':True},
        {'name':'Return', 'label':'RETURN %', 'field':'Return', 'align':'right', 'sortable':True},
    ]

    table = ui.table(columns=cols, rows=processed).classes('w-full border-slate-700')
    table.props("dark flat dense")
    
    table.add_slot('body-cell-Profit', r'''<q-td :props="props" :class="props.value.includes('+')?'text-green-400 font-mono font-bold':'text-red-400 font-mono font-bold'">{{props.value}}</q-td>''')
    table.add_slot('body-cell-Return', r'''<q-td :props="props" :class="props.value.includes('+')?'text-green-400 font-mono':'text-red-400 font-mono'">{{props.value}}</q-td>''')
    table.add_slot('body-cell-Ticker', r'''<q-td :props="props"><a :href="'/detail/'+props.value" class="text-blue-400 font-bold no-underline">{{props.value}}</a></q-td>''')