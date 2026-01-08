from nicegui import ui, app
from logic import score_universe_data, is_favorite, toggle_favorite
from universe import COMPANIES
from theme import frame
import pandas as pd
import plotly.express as px

def render_home():
    if "market" not in app.storage.user: app.storage.user["market"] = "USA"
    market = app.storage.user["market"]
    cur = "₹" if market == "INDIA" else "$"

    with frame(f"Home - {market}"):
        
        # --- Sidebar ---
        with ui.left_drawer(value=True).classes("bg-slate-900 p-4 border-r border-slate-800") as drawer:
            ui.label("Market").classes("text-xs font-bold text-slate-400 uppercase mb-2")
            with ui.row().classes("w-full gap-2 mb-6 no-wrap"):
                def set_m(m): app.storage.user["market"] = m; ui.navigate.reload()
                act = "bg-blue-600 text-white border-blue-500 shadow-md shadow-blue-900/20"
                inact = "bg-slate-800 text-slate-400 border-slate-700 hover:bg-slate-700"
                ui.button("🇺🇸 USA", on_click=lambda: set_m("USA")).classes(f"w-1/2 border transition-all {act if market=='USA' else inact}")
                ui.button("🇮🇳 INDIA", on_click=lambda: set_m("INDIA")).classes(f"w-1/2 border transition-all {act if market=='INDIA' else inact}")

            ui.label("Profile").classes("text-xs font-bold text-slate-400 uppercase mb-2")
            profile_select = ui.select(["TRADER", "SWING"], value="TRADER", label="Strategy").classes("w-full mb-4 bg-slate-800 rounded")
            
            ui.label("Filters").classes("text-xs font-bold text-slate-400 uppercase mb-2")
            s_opts = ["All"] + sorted(list(set([c["sector"] for c in COMPANIES if c.get("sector")])))
            sector_select = ui.select(s_opts, value="All", label="Sector").classes("w-full mb-4 bg-slate-800 rounded")
            
            search_opts = []
            for c in COMPANIES:
                if str(c.get("market", "USA")).upper() == market:
                    search_opts.append(f"{c['ticker']} - {c['name']}")
            search_select = ui.select(search_opts, label="Search Company", with_input=True, clearable=True).classes("w-full mb-4 bg-slate-800 rounded")
            
            lookback_slider = ui.slider(min=30, max=365, value=120).props("label-always color=blue-500")
            ui.button("Apply Filters", on_click=lambda: update_ui()).classes("w-full mt-8 bg-green-600 hover:bg-green-500 text-white shadow-lg font-bold transition-all")

        # --- Main Content ---
        with ui.column().classes("w-full max-w-full mx-auto p-4 gap-6"):
            
            # Sidebar Toggle
            with ui.row().classes("items-center gap-2"):
                ui.button(icon='menu', on_click=lambda: drawer.toggle()).props("flat color=white dense round").tooltip("Toggle Filters")
                ui.badge(market, color="blue").props("outline")

            content = ui.column().classes("w-full gap-6")

            def update_ui():
                content.clear()
                with content: 
                    ui.spinner("dots").classes("size-10 self-center text-slate-500")
                ui.timer(0.1, lambda: run_calculation(), once=True)

            def run_calculation():
                filtered = [c for c in COMPANIES if str(c.get("market", "USA")).upper() == market]
                if sector_select.value != "All": filtered = [c for c in filtered if c.get("sector") == sector_select.value]
                if search_select.value:
                    search_ticker = search_select.value.split(" - ")[0]
                    filtered = [c for c in filtered if c["ticker"] == search_ticker]
                
                df = score_universe_data(filtered, lookback_slider.value, profile_select.value)
                
                content.clear()
                
                if df.empty:
                    with content: ui.label("No data found.").classes("text-red-400 font-mono text-xl")
                    return

                with content:
                    # --- 1. Enhanced Banner ---
                    up_trend = df["Long"].astype(str).str.contains("Uptrend").mean() * 100
                    invest_count = df[df["Framework"] == "INVEST"].shape[0]
                    advancing = df[df["Change"] > 0].shape[0]
                    declining = df[df["Change"] < 0].shape[0]
                    
                    with ui.card().classes("w-full bg-slate-800 border-l-4 border-blue-500 p-4 shadow-lg"):
                        with ui.row().classes("w-full justify-between items-center wrap"):
                            with ui.column().classes("gap-0"):
                                ui.label(f"Market Regime: {market}").classes("text-xl font-black text-white tracking-tight")
                                ui.label(f"{up_trend:.0f}% Uptrends • {invest_count} Investable").classes("text-sm font-bold text-blue-300 font-mono")
                            
                            with ui.row().classes("gap-2"):
                                ui.badge(f"{advancing} Advancing", color="green").props("outline")
                                ui.badge(f"{declining} Declining", color="red").props("outline")

                    # --- 2. Sector Heat (Fixed Block) ---
                    if "Sector" in df.columns:
                        sector_perf = df.groupby("Sector")['Change%'].median().sort_values(ascending=False)
                        ui.label("Sector Heat").classes("text-xs font-bold text-slate-400 uppercase mt-2")
                        with ui.row().classes("w-full flex-wrap gap-2 border-b border-slate-800 pb-4"):
                            for sec, val in sector_perf.items():
                                col = "green" if val > 0 else ("red" if val < 0 else "grey")
                                with ui.element('div').classes(f"px-3 py-1.5 rounded-md border border-{col}-500/50 bg-{col}-500/10 flex items-center gap-2 cursor-default"):
                                    ui.label(sec).classes("text-xs font-bold text-white")
                                    ui.label(f"{val:+.2f}%").classes(f"text-xs font-mono text-{col}-400")

                    # --- 3. Snapshot Cards (FIXED ALIGNMENT) ---
                    ui.label("Top Opportunities").classes("text-2xl font-black text-white tracking-tight mt-2")
                    df_sorted = df.sort_values(by="Score", ascending=False)
                    
                    with ui.grid().classes("w-full gap-4 grid-cols-1 md:grid-cols-2 lg:grid-cols-4 mb-2"):
                        for _, row in df_sorted.head(4).iterrows():
                            # Styling
                            is_buy = row["Decision"] == "BUY"
                            is_wait = row["Decision"] == "WAIT"
                            bg_cls = "bg-gradient-to-br from-green-900/50 to-slate-900 border-green-500" if is_buy else ("bg-gradient-to-br from-yellow-900/40 to-slate-900 border-yellow-600/50" if is_wait else "bg-gradient-to-br from-red-900/50 to-slate-900 border-red-500")
                            
                            ma_dist = row.get("DistMA20", 0.0)
                            ma_color = "text-green-300" if ma_dist > 0 else "text-red-300"
                            ma_arrow = "⚡" if ma_dist > 0 else "❄️"
                            
                            chg = row['Change']
                            chg_pct = row['Change%']
                            txt_col = "text-green-400" if chg > 0 else "text-red-400"
                            arrow = "▲" if chg > 0 else "▼"

                            # CARD CONTAINER (Fixed 280px Height)
                            with ui.card().classes(f"p-4 border shadow-xl {bg_cls} h-[280px] flex flex-col justify-between hover:scale-[1.02] transition-transform duration-200"):
                                
                                # --- TOP SECTION ---
                                with ui.column().classes("w-full gap-0"):
                                    with ui.row().classes("w-full justify-between items-start no-wrap"):
                                        # TICKER FIX: min-h to reserve 2 lines, line-clamp-2 to wrap properly
                                        ui.label(row["Ticker"]).classes("text-xl font-black text-white tracking-tight leading-tight line-clamp-2 w-2/3 min-h-[3.25rem]")
                                        
                                        # PRICE: Pushed to right
                                        ui.label(f"{cur}{row['Last Close']:.2f}").classes("text-lg font-bold text-white/90 font-mono text-right w-1/3")

                                    with ui.row().classes("w-full justify-end items-center gap-1"):
                                         ui.label(f"{arrow} {chg:+.2f} ({chg_pct:+.2f}%)").classes(f"text-sm font-bold font-mono {txt_col}")

                                ui.separator().classes("bg-white/10")

                                # --- MIDDLE SECTION ---
                                with ui.column().classes("w-full gap-2"):
                                    with ui.row().classes("w-full justify-between items-center"):
                                        ui.label("Trend Intensity").classes("text-[10px] font-bold text-slate-400 uppercase")
                                        ui.label(f"{ma_arrow} {ma_dist:+.1f}%").classes(f"text-xs font-bold {ma_color}")
                                    
                                    with ui.row().classes("w-full justify-between items-center"):
                                        d_col = "green" if is_buy else ("orange" if is_wait else "red")
                                        ui.badge(row["Decision"], color=d_col).props("outline").classes("font-bold text-sm px-2")
                                        
                                        with ui.row().classes("gap-1 items-center cursor-pointer"):
                                            ui.label("SCORE").classes("text-[10px] font-bold text-slate-500")
                                            ui.label(f"{row['Score']:.0f}").classes("text-lg font-black text-white font-mono")
                                            with ui.icon("info_outline", color="slate-500").classes("text-[12px] hover:text-white"):
                                                 with ui.menu().classes("bg-slate-900 border border-slate-700 p-2"):
                                                    ui.label("Score Logic:").classes("text-xs font-bold text-white")
                                                    ui.label("• 45: Strong Trend").classes("text-xs text-slate-300")
                                                    ui.label("• +10: Active Buy").classes("text-xs text-green-400")
                                
                                # --- BOTTOM SECTION ---
                                ui.button("Open", on_click=lambda t=row["Ticker"]: ui.navigate.to(f'/detail/{t}')).props("flat dense").classes("w-full mt-auto text-white/50 hover:text-white hover:bg-white/10")

                    # --- 4. Tabs & Table ---
                    with ui.tabs().classes('w-full text-white bg-slate-800/50 rounded-t-lg') as tabs:
                        tab_list = ui.tab('List View', icon='list')
                        tab_map = ui.tab('Market Map', icon='dashboard')

                    with ui.tab_panels(tabs, value=tab_list).classes('w-full bg-transparent'):
                        
                        # Tab 1: Full Table
                        with ui.tab_panel(tab_list).classes("p-0"):
                            tdf = df.copy()
                            
                            def fmt_arrow(val):
                                arrow = "▲" if val > 0 else ("▼" if val < 0 else "•")
                                return f"{arrow} {val:,.2f}"
                            tdf['Change_Str'] = tdf['Change'].apply(fmt_arrow)
                            
                            tdf['Last Close'] = tdf['Last Close'].apply(lambda x: f"{cur}{x:,.2f}")
                            tdf['Stop'] = tdf['Stop'].apply(lambda x: f"{cur}{x:.2f}" if pd.notna(x) else "—")
                            tdf['Target'] = tdf['Target'].apply(lambda x: f"{cur}{x:.2f}" if pd.notna(x) else "—")
                            tdf['Change%'] = tdf['Change%'].map('{:+.2f}%'.format)
                            tdf['Entry'] = tdf['Entry'].replace("", "—")
                            
                            def sort_prefix(val, best="INVEST", mid="WAIT"): return f"1~{val}" if val == best else (f"2~{val}" if val == mid else f"3~{val}")
                            tdf['Decision_Sort'] = tdf['Decision'].apply(lambda x: sort_prefix(x, "BUY", "WAIT"))
                            tdf['Framework_Sort'] = tdf['Framework'].apply(lambda x: sort_prefix(x, "INVEST", "WAIT"))
                            tdf['is_fav'] = tdf['Ticker'].apply(is_favorite)

                            cols = [
                                {'name':'Fav', 'label':'', 'field':'is_fav', 'align':'center', 'sortable':False},
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
                            table.props("dark flat dense row-key='Ticker' virtual-scroll :rows-per-page-options='[0]' style='height: 800px'")
                            
                            def handle_star_click(e):
                                row_data = e.args
                                ticker = row_data['Ticker']
                                toggle_favorite(ticker)
                                for r in table.rows:
                                    if r['Ticker'] == ticker:
                                        r['is_fav'] = not r['is_fav']
                                        break
                                table.update()
                                status = "Saved" if is_favorite(ticker) else "Removed"
                                color = "amber" if status == "Saved" else "grey"
                                ui.notify(f"{status} {ticker}", color=color)

                            table.add_slot('body-cell-Fav', r'''
                                <q-td :props="props">
                                    <q-btn flat dense round 
                                        :icon="props.row.is_fav ? 'star' : 'star_border'" 
                                        :color="props.row.is_fav ? 'amber' : 'grey'"
                                        @click.stop="$parent.$emit('star_click', props.row)" 
                                    />
                                </q-td>
                            ''')
                            table.on('star_click', handle_star_click)

                            table.add_slot('body-cell-Ticker', r'''<q-td :props="props"><a :href="'/detail/'+props.value" class="text-blue-400 font-bold no-underline hover:text-blue-300">{{props.value}}</a></q-td>''')
                            table.add_slot('body-cell-Decision', r'''<q-td :props="props"><q-badge :color="props.value.includes('BUY')?'green':(props.value.includes('AVOID')?'red':'orange')" text-color="white" class="font-bold">{{ props.value.split('~')[1] }}</q-badge></q-td>''')
                            table.add_slot('body-cell-Framework', r'''<q-td :props="props"><q-badge :color="props.value.includes('INVEST')?'green':(props.value.includes('AVOID')?'red':'orange')" text-color="white">{{ props.value.split('~')[1] }}</q-badge></q-td>''')
                            table.add_slot('body-cell-Change%', r'''<q-td :props="props" :class="props.value.startsWith('+')?'text-green-400 font-mono':(props.value.startsWith('-')?'text-red-400 font-mono':'text-slate-400 font-mono')">{{props.value}}</q-td>''')
                            table.add_slot('body-cell-Change_Str', r'''<q-td :props="props" :class="props.value.includes('▲')?'text-green-400 font-mono':(props.value.includes('▼')?'text-red-400 font-mono':'text-slate-400 font-mono')">{{props.value}}</q-td>''')

                        # Tab 2: Map
                        with ui.tab_panel(tab_map).classes("p-0 min-h-[650px]"):
                            df_map = df.copy()
                            df_map["Size"] = df_map["Volume"].replace(0, 1)
                            df_map["MapLabel"] = df_map.apply(lambda x: f"<b>{x['Ticker']}</b><br>{x['Change%']:+.2f}%", axis=1)
                            
                            fig = px.treemap(
                                df_map, 
                                path=[px.Constant(market), 'Sector', 'Ticker'], 
                                values='Size',
                                color='Change%',
                                color_continuous_scale=[(0.0, '#F63538'), (0.5, '#303030'), (1.0, '#30CC5A')],
                                range_color=[-3, 3],
                                custom_data=['Company', 'Last Close', 'Decision']
                            )
                            
                            fig.update_traces(
                                text=df_map["MapLabel"], textinfo="text",
                                hovertemplate=f"<b>%{{label}}</b><br>%{{customdata[0]}}<br>Price: {cur}%{{customdata[1]}}<br>Signal: %{{customdata[2]}}<extra></extra>",
                                textposition="middle center", textfont=dict(family="Inter", size=14, color="white")
                            )
                            fig.update_layout(margin=dict(t=0, l=0, r=0, b=0), paper_bgcolor="#0f172a", plot_bgcolor="#0f172a", coloraxis_showscale=False)
                            
                            plot = ui.plotly(fig).classes("w-full h-[800px] rounded-lg border border-slate-700 shadow-2xl")
                            plot.on('plotly_click', lambda e: ui.navigate.to(f'/detail/{e.args["points"][0]["label"]}') if 'points' in e.args and 'label' in e.args['points'][0] and e.args['points'][0]['label'] in df_map['Ticker'].values else None)

            ui.timer(0.1, update_ui, once=True)