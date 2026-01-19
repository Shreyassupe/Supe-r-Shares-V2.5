from nicegui import ui, app
from universe import COMPANIES
from logic import fetch_news
from contextlib import contextmanager

@contextmanager
def frame(title):
    # --- GLOBAL STYLING: Force zero margins/padding ---
    ui.add_head_html('''
        <style>
            body { margin: 0; padding: 0; background-color: #0b0f19; }
            .nicegui-content { padding: 0 !important; margin: 0 !important; width: 100%; }
            .q-page-container { padding-top: 0 !important; padding-bottom: 0 !important; }
        </style>
    ''')
    
    # --- HEADER LOGIC ---
    if "market" not in app.storage.user: app.storage.user["market"] = "USA"
    if "profile" not in app.storage.user: app.storage.user["profile"] = "TRADER"
    if "sector_filter" not in app.storage.user: app.storage.user["sector_filter"] = "All"
    
    market = app.storage.user["market"]

    # --- ACTIONS ---
    def refresh_page():
        ui.navigate.reload()

    def set_market(m):
        app.storage.user["market"] = m
        app.storage.user["sector_filter"] = "All"
        refresh_page()

    def set_profile(p):
        app.storage.user["profile"] = p
        refresh_page()

    def set_sector(s):
        app.storage.user["sector_filter"] = s
        refresh_page()

    def handle_search(e):
        if e.value:
            ticker = e.value.split(" - ")[0]
            ui.navigate.to(f'/detail/{ticker}')
            app.storage.user["search_ticker"] = None

    # --- DRAWER (Keep outside the main column) ---
    with ui.right_drawer(value=False).classes("bg-slate-900 p-4 border-l border-slate-800") as right_drawer:
        ui.label("Headlines").classes("text-lg font-bold text-white mb-4")
        proxy = "SPY" if market == "USA" else "^NSEI"
        try:
            news = fetch_news(proxy, limit=10)
            if news:
                with ui.column().classes("gap-4"):
                    for item in news:
                        if item.get('title'):
                            with ui.card().classes("bg-slate-800 border border-slate-700 p-3 w-full"):
                                ui.label(item.get('publisher', 'News')).classes("text-[10px] font-bold text-blue-400 uppercase")
                                ui.link(item.get('title'), item.get('link'), new_tab=True).classes("text-sm font-bold text-white no-underline hover:text-blue-300 leading-snug")
            else: ui.label("No news.").classes("text-slate-500 italic")
        except: ui.label("News unavailable.").classes("text-slate-500 italic")

    # --- MAIN CONTAINER (Wrapper for everything) ---
    # We use a single column for the whole page. Header is just the first Row in it.
    with ui.column().classes('w-full min-h-screen bg-[#0b0f19] p-0 m-0 gap-0'):
        
        # --- MANUAL HEADER ROW (Zero Gap Guaranteed) ---
        with ui.row().classes('w-full h-16 bg-slate-900 border-b border-slate-800 px-4 flex items-center justify-between sticky top-0 z-50 no-wrap'):
            
            # 1. LEFT: Logo & Market
            with ui.row().classes('items-center gap-4'):
                with ui.row().classes('items-center gap-2 cursor-pointer').on('click', lambda: ui.navigate.to('/')):
                    ui.icon('show_chart', color='green-400').classes('text-2xl')
                    ui.label('Supe(r)Shares').classes('text-xl font-black text-white tracking-tight')
                
                ui.separator().props('vertical').classes('h-6 bg-slate-700')

                with ui.row().classes("gap-0 border border-slate-700 rounded overflow-hidden"):
                    btn_cls = "px-3 py-1 text-xs font-bold cursor-pointer transition-colors"
                    act_cls = "bg-blue-600 text-white"
                    inact_cls = "bg-slate-800 text-slate-400 hover:bg-slate-700"
                    ui.label("🇺🇸 USA").classes(f"{btn_cls} {act_cls if market=='USA' else inact_cls}").on("click", lambda: set_market("USA"))
                    ui.label("🇮🇳 INDIA").classes(f"{btn_cls} {act_cls if market=='INDIA' else inact_cls}").on("click", lambda: set_market("INDIA"))

            # 2. MIDDLE: Strategy & Search
            with ui.row().classes('items-center gap-3 flex-1 justify-center'):
                ui.select(["TRADER", "SWING"], value=app.storage.user["profile"], on_change=lambda e: set_profile(e.value)).props("dense options-dense borderless").classes("w-28 text-xs font-bold text-blue-400 bg-slate-800 px-2 rounded")
                
                s_opts = ["All"] + sorted(list(set([c["sector"] for c in COMPANIES if c.get("sector")])))
                ui.select(s_opts, value=app.storage.user["sector_filter"], on_change=lambda e: set_sector(e.value)).props("dense options-dense outlined rounded placeholder='Sector'").classes("w-40 bg-slate-800 text-xs")

                search_opts = [f"{c['ticker']} - {c['name']}" for c in COMPANIES if str(c.get("market", "USA")).upper() == market]
                ui.select(search_opts, value=app.storage.user.get("search_ticker"), on_change=handle_search, with_input=True, clearable=True, label="Search").props("dense outlined rounded search input-class='text-white'").classes("w-64 bg-slate-800")

            # 3. RIGHT: Nav Links & Tools
            with ui.row().classes('items-center gap-6'):
                ui.button(icon="refresh", on_click=refresh_page).props("round dense flat color=green").tooltip("Refresh Data")
                ui.button(icon="newspaper", on_click=lambda: right_drawer.toggle()).props("round dense flat color=blue").tooltip("Headlines")
                
                ui.separator().props('vertical').classes('h-6 bg-slate-700')

                def nav_link(text, target):
                    ui.link(text, target).classes('text-sm font-bold text-slate-400 no-underline hover:text-white transition-colors')
                
                nav_link('Home', '/')
                nav_link('Portfolio', '/portfolio')
                nav_link('Favorites', '/favorites')
                nav_link('Detail', '#')

        # --- CONTENT INJECTION POINT ---
        # No extra padding here ensures it touches the header
        with ui.column().classes('w-full p-0 m-0 gap-0'):
            yield
