from nicegui import ui, app
import os

# -------------------------------------------------------------------
# GLOBAL STYLE: Professional Font (Inter)
# -------------------------------------------------------------------
ui.add_head_html(r'''
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
<style>
    body, .q-app, .q-table, .q-btn, .q-item {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif !important;
    }
    .text-5xl, .text-4xl, .text-3xl, .text-2xl, .text-xl, .text-lg {
        font-weight: 700 !important;
        letter-spacing: -0.02em !important;
    }
</style>
''', shared=True)

# -------------------------------------------------------------------
# Imports & Page Routing
# -------------------------------------------------------------------
from home_page import render_home
from detail_page import render_detail
from favorites_page import render_favorites
from portfolio_page import render_portfolio  # <--- IMPORT THIS

@ui.page("/")
def index_page():
    render_home()

@ui.page("/portfolio") # <--- REGISTER THIS ROUTE
def portfolio_page_route():
    render_portfolio()

@ui.page("/detail/{ticker}")
def detail_page_route(ticker: str):
    render_detail(ticker)

@ui.page("/favorites")
def favorites_page_route():
    render_favorites()

# -------------------------------------------------------------------
# Execution
# -------------------------------------------------------------------
if __name__ in {"__main__", "__mp_main__"}:
    ui.run(
        title="SuperShares",
        host="0.0.0.0",
        port=8080,
        storage_secret="SUPERSHARES_SECRET_KEY_777",
        favicon="🚀",
        dark=True,
        reload=False
    )