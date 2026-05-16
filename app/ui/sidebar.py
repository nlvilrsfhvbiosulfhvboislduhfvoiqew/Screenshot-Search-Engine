import customtkinter as ctk
from typing import Callable

class Sidebar(ctk.CTkFrame):
    def __init__(self, master, on_nav_click: Callable[[str], None], **kwargs):
        super().__init__(master, corner_radius=0, **kwargs)
        self.on_nav_click = on_nav_click
        
        # App Logo / Title
        self.logo_label = ctk.CTkLabel(self, text="Search Engine", font=ctk.CTkFont(size=20, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))

        # Navigation Buttons
        self.btn_search = ctk.CTkButton(self, text="Search", fg_color="transparent", text_color=("gray10", "gray90"), 
                                        hover_color=("gray70", "gray30"), anchor="w",
                                        command=lambda: self.on_nav_click("search"))
        self.btn_search.grid(row=1, column=0, padx=20, pady=10, sticky="ew")

        self.btn_settings = ctk.CTkButton(self, text="Settings", fg_color="transparent", text_color=("gray10", "gray90"), 
                                          hover_color=("gray70", "gray30"), anchor="w",
                                          command=lambda: self.on_nav_click("settings"))
        self.btn_settings.grid(row=2, column=0, padx=20, pady=10, sticky="ew")

        # Reindex Button at bottom
        self.btn_reindex = ctk.CTkButton(self, text="Force Re-Index", command=lambda: self.on_nav_click("reindex"))
        self.btn_reindex.grid(row=5, column=0, padx=20, pady=(10, 20), sticky="s")
        
        # Configure rows to push the bottom button down
        self.grid_rowconfigure(4, weight=1)

    def set_active(self, page_name: str):
        """Highlights the active navigation button."""
        # Reset all
        self.btn_search.configure(fg_color="transparent")
        self.btn_settings.configure(fg_color="transparent")
        
        # Set active
        active_color = ("gray75", "gray25")
        if page_name == "search":
            self.btn_search.configure(fg_color=active_color)
        elif page_name == "settings":
            self.btn_settings.configure(fg_color=active_color)
