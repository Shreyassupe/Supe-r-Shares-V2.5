from nicegui import ui
from theme import frame
from logic import score_portfolio
from portfolio_manager import load_portfolio, remove_from_portfolio
import pandas as pd

def render_portfolio():
    with frame("My Portfolio"):
        with ui.column().classes("w-full max-w-full mx-auto p-4 gap-6"):
            
            # Header with Summary Stats
            portfolio_data = load_portfolio()
            
            if not portfolio_data:
                ui.label("Portfolio is Empty").classes("text-3xl font-black text-white")
                ui.label("Go to Home to add stocks.").classes("text-slate-400")
                ui.button("Go to Home", on_click=lambda: ui.navigate.to("/")).props("outline color=white")
                return

            # Calculate live data
            df = score_portfolio(portfolio_data)
            
            if df.empty:
                ui.label("Loading Market Data...").classes("text-xl text-slate-400")
                return

            # Summary Metrics
            total_invested = df["Invested"].sum()
            current_value = df["CurrentVal"].sum()
            total_pl = current_value - total_invested
            total_pl_pct = (total_pl / total_invested * 100) if total_invested > 0 else 0
            
            pl_color = "text-green-400" if total_pl >= 0 else "text-red-400"
            
            with ui.row().classes("w-full justify-between items-end border-b border-slate-800 pb-4"):
                ui.label("My Portfolio").classes("text-3xl font-black text-white")
                with ui.column().classes("items-end gap-0"):
                    ui.label("Total Net Worth").classes("text-xs font-bold text-slate-400 uppercase")
                    ui.label(f"${current_value:,.2f}").classes(f"text-3xl font-black {pl_color}")
                    ui.label(f"{total_pl:+,.2f} ({total_pl_pct:+.2f}%)").classes(f"text-sm font-mono font-bold {pl_color}")

            # Main Table
            def fmt_money(val): return f"${val:,.2f}"
            def fmt_pct(val): return f"{val:+.2f}%"
            
            # Formatting for display
            df["Invested"] = df["Invested"].apply(fmt_money)
            df["CurrentVal"] = df["CurrentVal"].apply(fmt_money)
            df["P&L_Str"] = df.apply(lambda x: f"{fmt_money(x['P&L'])} ({fmt_pct(x['P&L%'])})", axis=1)
            df["AvgPrice"] = df["AvgPrice"].apply(fmt_money)
            df["CurrentPrice"] = df["CurrentPrice"].apply(fmt_money)

            cols = [
                {'name':'Action', 'label':'', 'field':'Ticker', 'align':'center'},
                {'name':'Ticker', 'label':'TICKER', 'field':'Ticker', 'sortable':True, 'align':'left'},
                {'name':'Company', 'label':'COMPANY', 'field':'Company', 'sortable':True, 'align':'left'},
                {'name':'Qty', 'label':'QTY', 'field':'Qty', 'sortable':True, 'align':'center'},
                {'name':'AvgPrice', 'label':'AVG PRICE', 'field':'AvgPrice', 'align':'right'},
                {'name':'CurrentPrice', 'label':'PRICE', 'field':'CurrentPrice', 'align':'right'},
                {'name':'Invested', 'label':'INVESTED', 'field':'Invested', 'align':'right', 'sortable':True},
                {'name':'CurrentVal', 'label':'VALUE', 'field':'CurrentVal', 'align':'right', 'sortable':True},
                {'name':'P&L_Str', 'label':'PROFIT / LOSS', 'field':'P&L_Str', 'align':'right', 'sortable':True},
                {'name':'Decision', 'label':'ADVICE', 'field':'Decision', 'sortable':True, 'align':'center'},
            ]
            
            table = ui.table(columns=cols, rows=df.to_dict("records")).classes('w-full border-slate-700')
            table.props("dark flat dense row-key='Ticker'")

            # Slots for Styling
            
            # 1. P&L Color Coding
            table.add_slot('body-cell-P&L_Str', r'''
                <q-td :props="props" :class="props.value.includes('+')?'text-green-400 font-mono font-bold':'text-red-400 font-mono font-bold'">
                    {{props.value}}
                </q-td>
            ''')

            # 2. Advice Column (SELL WARNING in Red)
            table.add_slot('body-cell-Decision', r'''
                <q-td :props="props">
                    <q-badge :color="props.value === 'SELL WARNING' ? 'red' : (props.value === 'BUY' ? 'green' : 'orange')" 
                             :label="props.value" 
                             class="font-bold text-xs p-2" />
                </q-td>
            ''')
            
            # 3. Delete Button
            def handle_delete(e):
                remove_from_portfolio(e.args["Ticker"])
                ui.navigate.reload()

            table.add_slot('body-cell-Action', r'''
                <q-td :props="props">
                    <q-btn flat dense round icon="delete" color="red" size="sm" @click.stop="$parent.$emit('del', props.row)" />
                </q-td>
            ''')
            table.on('del', handle_delete)
            
            table.add_slot('body-cell-Ticker', r'''<q-td :props="props"><a :href="'/detail/'+props.value" class="text-blue-400 font-bold no-underline">{{props.value}}</a></q-td>''')