from nicegui import ui, app
from logic import score_universe_data, get_favorites, toggle_favorite
from universe import COMPANIES
from theme import frame
import pandas as pd

def render_favorites():
    with frame("Favorites"):
        with ui.column().classes("w-full max-w-full mx-auto p-4 gap-6"):
            
            ui.label("My Favorites").classes("text-3xl font-black text-white")
            
            content = ui.column().classes("w-full gap-6")

            def update():
                content.clear()
                favs = get_favorites()
                
                if not favs:
                    with content:
                        ui.label("No favorites yet.").classes("text-xl text-slate-400")
                        ui.label("Go to Home, search for a stock, and click the star to add it.").classes("text-slate-500")
                        ui.button("Go to Home", on_click=lambda: ui.navigate.to("/")).props("outline color=white")
                    return

                my_companies = [c for c in COMPANIES if c["ticker"] in favs]
                
                with content:
                    ui.spinner("dots").classes("size-10 self-center text-slate-500")

                df = score_universe_data(my_companies, lookback_days=120, profile="TRADER")
                
                content.clear()
                if df.empty: return

                with content:
                    tdf = df.copy()
                    
                    def fmt_arrow(val):
                        arrow = "▲" if val > 0 else ("▼" if val < 0 else "•")
                        return f"{arrow} {val:,.2f}"
                    tdf['Change_Str'] = tdf['Change'].apply(fmt_arrow)
                    
                    tdf['Last Close'] = tdf['Last Close'].map('${:,.2f}'.format)
                    tdf['Change%'] = tdf['Change%'].map('{:+.2f}%'.format)
                    tdf['Stop'] = tdf['Stop'].apply(lambda x: f"${x:.2f}" if pd.notna(x) else "—")
                    tdf['Target'] = tdf['Target'].apply(lambda x: f"${x:.2f}" if pd.notna(x) else "—")
                    tdf['Entry'] = tdf['Entry'].replace("", "—")
                    
                    def sort_prefix(val, best="INVEST", mid="WAIT"):
                        return f"1~{val}" if val == best else (f"2~{val}" if val == mid else f"3~{val}")
                    tdf['Decision_Sort'] = tdf['Decision'].apply(lambda x: sort_prefix(x, "BUY", "WAIT"))
                    tdf['Framework_Sort'] = tdf['Framework'].apply(lambda x: sort_prefix(x, "INVEST", "WAIT"))

                    cols = [
                        {'name':'Fav', 'label':'', 'field':'Ticker', 'align':'center', 'sortable':False},
                        {'name':'Ticker', 'label':'TICKER', 'field':'Ticker', 'sortable':True, 'align':'left'},
                        {'name':'Company', 'label':'COMPANY', 'field':'Company', 'sortable':True, 'align':'left'},
                        {'name':'Last Close', 'label':'PRICE', 'field':'Last Close', 'align':'right', 'sortable':True},
                        {'name':'Change_Str', 'label':'Δ', 'field':'Change_Str', 'align':'right', 'sortable':True},
                        {'name':'Change%', 'label':'Δ%', 'field':'Change%', 'align':'right', 'sortable':True},
                        {'name':'Decision', 'label':'DECISION', 'field':'Decision_Sort', 'sortable':True, 'align':'center'},
                        {'name':'Conf', 'label':'CONF', 'field':'Conf', 'sortable':True, 'align':'center'},
                        {'name':'Entry', 'label':'ENTRY', 'field':'Entry', 'align':'left', 'sortable':True},
                        {'name':'Stop', 'label':'STOP', 'field':'Stop', 'align':'right'},
                        {'name':'Target', 'label':'TARGET', 'field':'Target', 'align':'right'},
                        {'name':'Framework', 'label':'FRAMEWORK', 'field':'Framework_Sort', 'sortable':True, 'align':'center'},
                        {'name':'Score', 'label':'SCORE', 'field':'Score', 'sortable':True, 'align':'center'},
                        {'name':'Short', 'label':'SHORT', 'field':'Short', 'align':'left'},
                        {'name':'Long', 'label':'LONG', 'field':'Long', 'align':'left'},
                        {'name':'Volatility', 'label':'VOL', 'field':'Volatility', 'align':'left'},
                    ]
                    
                    table = ui.table(columns=cols, rows=tdf.to_dict("records")).classes('w-full border-slate-700')
                    table.props("dark flat dense row-key='Ticker'")
                    
                    # Robust Extractor
                    def _extract_ticker(e):
                        arg = e.args
                        if isinstance(arg, str): return arg
                        if isinstance(arg, list) and len(arg) > 0: return str(arg[0])
                        if isinstance(arg, dict): return str(arg.get("Ticker"))
                        return None

                    def handle_remove_fav(e):
                        ticker = _extract_ticker(e)
                        if ticker:
                            toggle_favorite(ticker)
                            update() 
                            ui.notify(f"Removed {ticker}", color="red")

                    # Use safe emitter
                    table.add_slot('body-cell-Fav', r'''
                        <q-td :props="props">
                            <q-btn flat dense round icon="star" color="amber" @click.stop="(typeof emit === 'function' ? emit : $parent.$emit)('remove_fav', props.row.Ticker)" />
                        </q-td>
                    ''')
                    table.on('remove_fav', handle_remove_fav)

                    table.add_slot('body-cell-Ticker', r'''<q-td :props="props"><a :href="'/detail/'+props.value" class="text-blue-400 font-bold no-underline">{{props.value}}</a></q-td>''')
                    table.add_slot('body-cell-Decision', r'''<q-td :props="props"><q-badge :color="props.value.includes('BUY')?'green':(props.value.includes('AVOID')?'red':'orange')" text-color="white" class="font-bold">{{ props.value.split('~')[1] }}</q-badge></q-td>''')
                    table.add_slot('body-cell-Framework', r'''<q-td :props="props"><q-badge :color="props.value.includes('INVEST')?'green':(props.value.includes('AVOID')?'red':'orange')" text-color="white">{{ props.value.split('~')[1] }}</q-badge></q-td>''')
                    table.add_slot('body-cell-Change%', r'''<q-td :props="props" :class="props.value.startsWith('+')?'text-green-400 font-mono':(props.value.startsWith('-')?'text-red-400 font-mono':'text-slate-400 font-mono')">{{props.value}}</q-td>''')
                    table.add_slot('body-cell-Change_Str', r'''<q-td :props="props" :class="props.value.includes('▲')?'text-green-400 font-mono':(props.value.includes('▼')?'text-red-400 font-mono':'text-slate-400 font-mono')">{{props.value}}</q-td>''')

            update()