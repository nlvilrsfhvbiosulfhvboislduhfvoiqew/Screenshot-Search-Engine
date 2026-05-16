import customtkinter as ctk
from typing import Callable, Any, Dict

from app.database.db_manager import DatabaseManager
from app.search.engine import SearchEngine
from app.ui.sidebar import Sidebar
from app.ui.image_grid import ImageGrid
from app.ui.preview_panel import PreviewPanel
from app.ui.settings_page import SettingsPage

class MainWindow(ctk.CTk):
    def __init__(self, db_manager: DatabaseManager, search_engine: SearchEngine, 
                 on_folder_added: Callable[[str], None], 
                 on_folder_removed: Callable[[str], None],
                 on_force_reindex: Callable[[], None]):
        super().__init__()

        self.db = db_manager
        self.search_engine = search_engine
        
        # Window configuration
        self.title("Screenshot Search Engine")
        self.geometry("1100x700")
        self.minsize(800, 600)
        
        # Apply theme from settings
        theme = self.db.get_setting("theme", "System")
        ctk.set_appearance_mode(theme)
        ctk.set_default_color_theme("blue")

        # Grid layout (1 row, 2 columns)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # 1. Sidebar
        self.sidebar = Sidebar(self, on_nav_click=self._handle_nav_click, width=200)
        self.sidebar.grid(row=0, column=0, sticky="nsew")

        # 2. Main Content Area
        self.main_container = ctk.CTkFrame(self, fg_color="transparent")
        self.main_container.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        self.main_container.grid_rowconfigure(1, weight=1)
        self.main_container.grid_columnconfigure(0, weight=1)

        # 2a. Search View (Default)
        self.search_view = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.search_view.grid(row=0, column=0, rowspan=2, sticky="nsew")
        self.search_view.grid_rowconfigure(1, weight=1)
        self.search_view.grid_columnconfigure(0, weight=1)

        # Top Bar (Search Input)
        self.top_bar = ctk.CTkFrame(self.search_view, fg_color="transparent")
        self.top_bar.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 10))
        self.top_bar.grid_columnconfigure(0, weight=1)

        self.search_entry = ctk.CTkEntry(self.top_bar, placeholder_text="Search screenshots (text, filename, tags)...", height=40)
        self.search_entry.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        self.search_entry.bind("<Return>", self._perform_search)

        self.btn_do_search = ctk.CTkButton(self.top_bar, text="Search", width=100, height=40, command=self._perform_search)
        self.btn_do_search.grid(row=0, column=1)

        # Middle Content (Grid + Preview)
        self.content_area = ctk.CTkFrame(self.search_view, fg_color="transparent")
        self.content_area.grid(row=1, column=0, sticky="nsew")
        self.content_area.grid_rowconfigure(0, weight=1)
        self.content_area.grid_columnconfigure(0, weight=1)

        self.image_grid = ImageGrid(self.content_area, on_image_click=self._show_preview)
        self.image_grid.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

        self.preview_panel = PreviewPanel(self.content_area, width=300)
        self.preview_panel.grid(row=0, column=1, sticky="ns")
        # Initially hide preview
        self.preview_panel.grid_remove()

        # 2b. Settings View
        self.settings_view = SettingsPage(
            self.main_container, 
            db_manager=self.db, 
            on_folder_added=on_folder_added,
            on_folder_removed=on_folder_removed
        )

        # State
        self.on_force_reindex = on_force_reindex
        
        # Load initial data
        self._handle_nav_click("search")
        self._load_initial_data()

    def _handle_nav_click(self, page_name: str):
        if page_name == "reindex":
            self.on_force_reindex()
            return
            
        self.sidebar.set_active(page_name)
        
        if page_name == "search":
            self.settings_view.grid_forget()
            self.search_view.grid(row=0, column=0, rowspan=2, sticky="nsew")
        elif page_name == "settings":
            self.search_view.grid_forget()
            self.settings_view.grid(row=0, column=0, rowspan=2, sticky="nsew")

    def _perform_search(self, event=None):
        query = self.search_entry.get()
        if query.strip():
            results = self.search_engine.search(query)
        else:
            # If empty, load all
            results = self.db.get_all_screenshots()
            
        self.image_grid.update_results(results)
        self.preview_panel.clear()
        self.preview_panel.grid_remove() # Hide preview when new search happens

    def _show_preview(self, data: Dict[str, Any]):
        self.preview_panel.grid(row=0, column=1, sticky="ns")
        self.preview_panel.load_image(
            path=data.get('path', ''),
            ocr_text=data.get('ocr_text', '')
        )

    def _load_initial_data(self):
        # Load recent screenshots on startup
        results = self.db.get_all_screenshots()
        # Limit to 50 for fast initial load
        self.image_grid.update_results(results[:50])

    def notify_new_image(self, file_path: str):
        """Called by the main app controller when a new image is indexed."""
        # Update the grid if we are on the main screen and search is empty
        # If user is searching, we don't interrupt them.
        if not self.search_entry.get().strip():
            self.after(0, self._load_initial_data)
