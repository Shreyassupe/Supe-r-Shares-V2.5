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
        
        # --- Clickable Logo (Redirects to Home) ---
        with ui.link(target="/").classes("flex items-center gap-2 no-underline text-white hover:text-green-400 transition-colors cursor-pointer"):
            ui.icon("show_chart").classes("text-2xl text-green-400")
            ui.label("SuperShares").classes("text-xl font-bold tracking-tight")

        # --- Navigation Links ---
        with ui.row().classes("gap-6"):
            # Helper for consistent link styling
            def nav_link(text, target):
                ui.link(text, target).classes("text-slate-300 no-underline hover:text-white font-medium")
            
            nav_link("Home", "/")
            nav_link("Portfolio", "/portfolio")  # <--- NEW LINK ADDED HERE
            nav_link("Favorites", "/favorites")
            nav_link("Detail", "/detail/SPY")

    # 3. Yield control back to the page
    yield