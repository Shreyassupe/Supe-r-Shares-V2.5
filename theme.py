from nicegui import ui
from contextlib import contextmanager

@contextmanager
def frame(page_title: str):
    """
    Wraps every page with a consistent Header and Title.
    """
    # 1. Force Dark Mode Globally
    ui.dark_mode().enable()
    
    # 2. The Top Navigation Bar (Darker Slate)
    with ui.header().classes("items-center justify-between bg-slate-950 text-white border-b border-slate-800"):
        
        # --- NEW: Clickable Logo (Redirects to Home) ---
        with ui.link(target="/").classes("flex items-center gap-2 no-underline text-white hover:text-green-400 transition-colors cursor-pointer"):
            ui.icon("show_chart").classes("text-2xl text-green-400")
            ui.label("SuperShares").classes("text-xl font-bold tracking-tight")

        with ui.row().classes("gap-6"):
            # Lighter hover effects
            ui.link("Home", "/").classes("text-slate-300 no-underline hover:text-white font-medium")
            ui.link("Detail", "/detail/SPY").classes("text-slate-300 no-underline hover:text-white font-medium")
            ui.link("Favorites", "/favorites").classes("text-slate-300 no-underline hover:text-white font-medium")

    # 3. Yield control back to the page
    yield