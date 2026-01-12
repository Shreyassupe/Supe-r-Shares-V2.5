from nicegui import ui, app
from logic import score_universe_data, is_favorite, toggle_favorite
from universe import COMPANIES
from theme import frame
from portfolio_manager import add_transaction, get_portfolio_tickers
import pandas as pd
import plotly.express as px
import sys

def render_home():
    if "market" not in app.storage.user: app.storage.user["market"] = "USA"
    market = app.storage.user["market"]
    cur = "₹" if market == "INDIA" else "$"

    # Sort State
    if "home_sort" not in app.storage.user:
        app.storage.user["home_sort"] = {"col": "Score", "asc": False}
    sort_state = app.storage.user["home_sort"]

    # --- CSS GRID LAYOUT (FIXED & WIDENED) ---
    # 1. Actions: 60px
    # 2. Ticker: 120px (Increased for INDIA)
    # 3. Company: 250px (Increased for Long Names)
    GRID_COLS = "60px 120px 250px 80px 80px 60px 90px 90px 60px 110px 70px 70px 50px 110px 70px 70px"
    GRID_CSS = f"display: grid; grid-template-columns: {GRID_COLS}; gap: 8px; align-items: center; padding-left: 0px; padding-right: 8px;"
    ROW_WIDTH = "min-w-[1600px]" # Adjusted total width

    with frame(f"Home - {market}"):
        
        # --- 1. POPUP DIALOG ---
        def open_buy_dialog(ticker, price_val):
            try:
                clean_price = float(price_val)
            except:
                clean_price = 0.0

            with ui.dialog() as dialog, ui.card().classes("bg-slate-900 border border-slate-700 w-96"):
                ui.label(f"Add {ticker}").classes("text-xl font-bold text-white mb-4")
                qty_input = ui.number(label="Shares", value=1, min=0.01).classes("w-full mb-2")
                price_input = ui.number(label="Price", value=clean_price, format="%.2f").classes("w-full mb-6")
                
                def save():
                    add_transaction(ticker, qty_input.value, price_input.value)
                    dialog.close()
                    ui.notify(f"Added {ticker}", color="green")
                    update_ui()
                    
                with ui.row().classes("w-full justify-end"):
                    ui.button("Cancel", on_click=dialog.close).props("flat color=grey")
                    ui.button("Add", on_click=save).props("color=green")
            dialog.open()

        # --- 2. SIDEBAR ---
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

        # --- 3. MAIN CONTENT ---
        with ui.column().classes("w-full max-w-full mx-auto p-4 gap-6"):
            
            # Header
            with ui.row().classes("w-full items-center justify-between"):
                with ui.row().classes("items-center gap-2"):
                    ui.button(icon='menu', on_click=lambda: drawer.toggle()).props("flat color=white dense round")
                    ui.label(f"{market} MARKET").classes("text-lg font-bold text-white tracking-wide")
                ui.badge(market, color="blue").props("outline")

            content = ui.column().classes("w-full gap-6")

            def update_ui():
                content.clear()
                with content: ui.spinner("dots").classes("size-10 self-center text-slate-500")
                ui.timer(0.1, lambda: run_calculation(), once=True)

            def run_calculation():
                filtered = [c for c in COMPANIES if str(c.get("market", "USA")).upper() == market]
                if sector_select.value != "All": filtered = [c for c in filtered if c.get("sector") == sector_select.value]
                if search_select.value:
                    s_val = search_select.value.split(" - ")[0]
                    filtered = [c for c in filtered if c["ticker"] == s_val]
                
                df = score_universe_data(filtered, lookback_slider.value, profile_select.value)
                content.clear()
                
                if df.empty:
                    with content: ui.label("No data found.").classes("text-red-400")
                    return

                with content:
                    # --- A. BANNER ---
                    up_trend = df["Long"].astype(str).str.contains("Uptrend").mean() * 100
                    invest_count = df[df["Framework"] == "INVEST"].shape[0]
                    with ui.card().classes("w-full bg-slate-800 border-l-4 border-blue-500 p-4 shadow-lg"):
                        with ui.row().classes("w-full justify-between items-center wrap"):
                            with ui.column().classes("gap-0"):
                                ui.label(f"Market Regime: {market}").classes("text-xl font-black text-white")
                                ui.label(f"{up_trend:.0f}% Uptrends • {invest_count} Investable").classes("text-sm font-bold text-blue-300 font-mono")
                            with ui.row().classes("gap-2"):
                                ui.badge(f"{df[df['Change']>0].shape[0]} Advancing", color="green").props("outline")
                                ui.badge(f"{df[df['Change']<0].shape[0]} Declining", color="red").props("outline")

                    # --- B. SECTOR CARDS ---
                    if "Sector" in df.columns:
                        sector_perf = df.groupby("Sector")['Change%'].median().sort_values(ascending=False)
                        with ui.grid().classes("w-full grid-cols-2 md:grid-cols-4 lg:grid-cols-8 gap-3"):
                            for sec, val in sector_perf.items():
                                col_cls = "text-green-400" if val > 0 else ("text-red-400" if val < 0 else "text-slate-400")
                                border_cls = "border-green-500/30" if val > 0 else ("border-red-500/30" if val < 0 else "border-slate-700")
                                bg_cls = "bg-green-500/5" if val > 0 else ("bg-red-500/5" if val < 0 else "bg-slate-800/50")
                                
                                with ui.card().classes(f"{bg_cls} border {border_cls} p-3 rounded-lg w-full hover:bg-slate-800 transition-all cursor-default shadow-sm"):
                                    with ui.column().classes("gap-1 items-start w-full"):
                                        ui.label(sec).classes("text-[10px] uppercase font-bold text-slate-400 tracking-wider truncate w-full")
                                        with ui.row().classes("items-center gap-1"):
                                            icon = "trending_up" if val > 0 else ("trending_down" if val < 0 else "remove")
                                            ui.icon(icon).classes(f"text-sm {col_cls}")
                                            ui.label(f"{val:+.2f}%").classes(f"text-lg font-black {col_cls} leading-none")

                    # --- C. SNAPSHOT CARDS ---
                    ui.label("Top Opportunities").classes("text-2xl font-black text-white tracking-tight mt-2")
                    df_sorted = df.sort_values(by="Score", ascending=False)
                    with ui.grid().classes("w-full gap-4 grid-cols-1 md:grid-cols-2 lg:grid-cols-4 mb-2"):
                        for _, row in df_sorted.head(4).iterrows():
                            is_buy = row["Decision"] == "BUY"
                            bg_cls = "bg-gradient-to-br from-green-900/50 to-slate-900 border-green-500" if is_buy else ("bg-gradient-to-br from-yellow-900/40 to-slate-900 border-yellow-600/50" if row["Decision"] == "WAIT" else "bg-gradient-to-br from-red-900/50 to-slate-900 border-red-500")
                            chg = row['Change']
                            chg_pct = row['Change%']
                            arrow = "▲" if chg > 0 else "▼"
                            txt_col = "text-green-400" if chg > 0 else "text-red-400"

                            with ui.card().classes(f"p-4 border shadow-xl {bg_cls} h-[280px] flex flex-col justify-between hover:scale-[1.02] transition-transform duration-200"):
                                with ui.column().classes("w-full gap-0"):
                                    with ui.row().classes("w-full justify-between items-start no-wrap"):
                                        ui.label(row["Ticker"]).classes("text-2xl font-black text-white tracking-tight")
                                        ui.label(f"{cur}{row['Last Close']:.2f}").classes("text-lg font-bold text-white/90 font-mono")
                                    ui.label(row["Company"]).classes("text-xs font-medium text-slate-400 truncate w-full mb-2")
                                    ui.label(f"{arrow} {chg:+.2f} ({chg_pct:+.2f}%)").classes(f"text-sm font-bold font-mono {txt_col}")
                                ui.separator().classes("bg-white/10")
                                with ui.column().classes("w-full gap-2"):
                                    with ui.row().classes("w-full justify-between items-center"):
                                        ui.label("Trend Intensity").classes("text-[10px] font-bold text-slate-400 uppercase")
                                        ui.label(f"{row.get('DistMA20',0):+.1f}%").classes(f"text-xs font-bold text-white")
                                    with ui.row().classes("w-full justify-between items-center"):
                                        d_col = "green" if is_buy else ("orange" if row["Decision"] == "WAIT" else "red")
                                        ui.badge(row["Decision"], color=d_col).props("outline").classes("font-bold text-sm px-2")
                                        with ui.row().classes("gap-1 items-center"):
                                            ui.label("SCORE").classes("text-[10px] font-bold text-slate-500")
                                            ui.label(f"{row['Score']:.0f}").classes("text-lg font-black text-white font-mono")
                                ui.button("Open", on_click=lambda t=row["Ticker"]: ui.navigate.to(f'/detail/{t}')).props("flat dense").classes("w-full mt-auto text-white/50 hover:text-white hover:bg-white/10")

                    # --- D. TABS & TABLE ---
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
                            
                            # Sort Logic
                            rank_map = {"BUY": 3, "INVEST": 3, "WAIT": 2, "AVOID": 1, "SELL WARNING": 0}
                            if sort_state['col'] in ["Decision", "Framework"]:
                                tdf["_Rank"] = tdf[sort_state['col']].map(lambda x: rank_map.get(x, 0))
                                tdf = tdf.sort_values(by="_Rank", ascending=sort_state['asc'])
                            elif sort_state['col'] in tdf.columns:
                                tdf = tdf.sort_values(by=sort_state['col'], ascending=sort_state['asc'])

                            def handle_sort(col_name):
                                if sort_state['col'] == col_name:
                                    sort_state['asc'] = not sort_state['asc']
                                else:
                                    sort_state['col'] = col_name
                                    if col_name in ["Score", "Last Close", "Change%", "Decision", "Framework"]:
                                        sort_state['asc'] = False 
                                    else:
                                        sort_state['asc'] = True 
                                app.storage.user["home_sort"] = sort_state
                                update_ui()

                            with ui.scroll_area().classes('h-[800px] w-full'):
                                # --- HEADER ---
                                with ui.element('div').classes(f'w-full border-b border-slate-600 bg-slate-900 sticky top-0 z-10 py-2 shadow-md {ROW_WIDTH}').style(GRID_CSS):
                                    def header(label, col_db=None, align="left"):
                                        base = f'text-{align} text-xs font-bold tracking-wider uppercase text-slate-400 select-none truncate'
                                        if col_db:
                                            color = "text-blue-400" if sort_state['col'] == col_db else "hover:text-slate-200 cursor-pointer"
                                            arrow = " ▼" if sort_state['col'] == col_db and not sort_state['asc'] else (" ▲" if sort_state['col'] == col_db else "")
                                            with ui.element('div').classes(f"{base} {color}").on('click', lambda: handle_sort(col_db)):
                                                ui.label(label + arrow)
                                        else:
                                            ui.label(label).classes(base)

                                    header('ACTIONS', align="center")
                                    header('TICKER', 'Ticker')
                                    header('COMPANY', 'Company')
                                    header('PRICE', 'Last Close', align="right")
                                    header('CHANGE', 'Change', align="right")
                                    header('%', 'Change%', align="right")
                                    header('DECISION', 'Decision', align="center")
                                    header('FRAMEWORK', 'Framework', align="center")
                                    header('CONF', 'Conf', align="center")
                                    header('ENTRY', 'Entry')
                                    header('STOP', 'Stop', align="right")
                                    header('TARGET', 'Target', align="right")
                                    header('SCORE', 'Score', align="center")
                                    header('SHORT', 'Short')
                                    header('LONG', 'Long')
                                    header('VOLATILITY', 'Volatility')

                                # --- ROWS ---
                                for _, row in tdf.iterrows():
                                    price_str = f"{cur}{row['Last Close']:,.2f}"
                                    chg = row['Change']
                                    chg_pct = row['Change%']
                                    arrow = "▲" if chg > 0 else "▼"
                                    chg_color = "text-green-400" if chg > 0 else "text-red-400"
                                    chg_str = f"{arrow} {chg:.2f}"
                                    pct_str = f"{chg_pct:+.2f}%"
                                    
                                    decision = row['Decision']
                                    dec_color = "green" if "BUY" in decision else ("red" if "AVOID" in decision else "orange")
                                    fw = row['Framework']
                                    fw_color = "green" if fw == "INVEST" else ("red" if fw == "AVOID" else "orange")

                                    stop_str = f"{cur}{row['Stop']:.2f}" if row['Stop'] > 0 else "—"
                                    tgt_str = f"{cur}{row['Target']:.2f}" if row['Target'] > 0 else "—"
                                    
                                    with ui.element('div').classes(f'w-full hover:bg-white/5 transition-colors border-b border-slate-800 py-1 {ROW_WIDTH}').style(GRID_CSS):
                                        
                                        with ui.row().classes('justify-center gap-1'):
                                            def click_fav(t=row['Ticker']):
                                                toggle_favorite(t)
                                                update_ui()
                                            ui.button(icon='star' if row['is_fav'] else 'star_border', 
                                                      color='amber' if row['is_fav'] else 'grey',
                                                      on_click=click_fav).props('flat dense round size=xs')
                                            
                                            def click_buy(t=row['Ticker'], p=row['Last Close']):
                                                open_buy_dialog(t, p)
                                            pf_col = 'blue-500' if row['is_owned'] else 'grey-700'
                                            pf_props = 'flat dense round size=xs' if row['is_owned'] else 'outline dense round size=xs'
                                            ui.button(icon='business_center', color=pf_col, on_click=click_buy).props(pf_props)

                                        ui.link(row['Ticker'], f"/detail/{row['Ticker']}").classes('text-sm font-bold text-blue-400 no-underline hover:text-white')
                                        ui.label(str(row['Company'])).classes('text-xs text-slate-300 truncate font-medium')
                                        ui.label(price_str).classes('text-right font-mono text-xs text-white')
                                        ui.label(chg_str).classes(f'{chg_color} text-right font-mono text-xs font-bold')
                                        ui.label(pct_str).classes(f'{chg_color} text-right font-mono text-xs')
                                        
                                        with ui.row().classes('justify-center'):
                                            ui.badge(decision, color=dec_color).props('outline').classes('font-bold text-[10px] px-1.5 py-0.5')
                                        
                                        with ui.row().classes('justify-center'):
                                            ui.badge(fw, color=fw_color).classes('text-[10px] px-1.5 py-0.5 font-bold text-white')

                                        ui.label(str(row['Conf'])).classes('text-center text-xs text-white')
                                        ui.label(str(row['Entry']) if row['Entry'] else "—").classes('text-left text-xs text-slate-400 truncate')
                                        ui.label(stop_str).classes('text-right font-mono text-xs text-red-400')
                                        ui.label(tgt_str).classes('text-right font-mono text-xs text-green-400')
                                        ui.label(f"{row['Score']:.0f}").classes('text-center text-sm font-bold text-white')
                                        ui.label(str(row['Short'])).classes('text-left text-[11px] text-slate-400 truncate')
                                        ui.label(str(row['Long'])).classes('text-left text-[11px] text-slate-400')
                                        ui.label(str(row['Volatility'])).classes('text-left text-[11px] text-slate-400')

                        with ui.tab_panel(tab_map).classes("p-0 min-h-[650px]"):
                            df_map = df.copy()
                            df_map["Size"] = df_map["Volume"].replace(0, 1)
                            df_map["MapLabel"] = df_map.apply(lambda x: f"<b>{x['Ticker']}</b><br>{x['Change%']:+.2f}%", axis=1)
                            fig = px.treemap(df_map, path=[px.Constant(market), 'Sector', 'Ticker'], values='Size', color='Change%', color_continuous_scale=[(0.0, '#F63538'), (0.5, '#303030'), (1.0, '#30CC5A')], range_color=[-3, 3], custom_data=['Company', 'Last Close', 'Decision'])
                            fig.update_traces(text=df_map["MapLabel"], textinfo="text", hovertemplate=f"<b>%{{label}}</b><br>%{{customdata[0]}}<br>Price: {cur}%{{customdata[1]}}<br>Signal: %{{customdata[2]}}<extra></extra>", textposition="middle center", textfont=dict(family="Inter", size=14, color="white"))
                            fig.update_layout(margin=dict(t=0, l=0, r=0, b=0), paper_bgcolor="#0f172a", plot_bgcolor="#0f172a", coloraxis_showscale=False)
                            plot = ui.plotly(fig).classes("w-full h-[800px] rounded-lg border border-slate-700 shadow-2xl")
                            plot.on('plotly_click', lambda e: ui.navigate.to(f'/detail/{e.args["points"][0]["label"]}') if 'points' in e.args and 'label' in e.args['points'][0] and e.args['points'][0]['label'] in df_map['Ticker'].values else None)

            ui.timer(0.1, update_ui, once=True)