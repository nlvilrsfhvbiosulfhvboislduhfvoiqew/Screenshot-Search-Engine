import customtkinter as ctk
import tkinter.filedialog as filedialog
from typing import Callable

from app.database.db_manager import DatabaseManager

class SettingsPage(ctk.CTkFrame):
    def __init__(self, master, db_manager: DatabaseManager, on_folder_added: Callable[[str], None], on_folder_removed: Callable[[str], None], **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        
        self.db = db_manager
        self.on_folder_added = on_folder_added
        self.on_folder_removed = on_folder_removed

        self.title_label = ctk.CTkLabel(self, text="Settings", font=ctk.CTkFont(size=24, weight="bold"))
        self.title_label.pack(anchor="w", pady=(20, 20), padx=20)

        # UI Theme Setting
        self.theme_frame = ctk.CTkFrame(self)
        self.theme_frame.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkLabel(self.theme_frame, text="UI Theme:").pack(side="left", padx=10, pady=10)
        self.theme_menu = ctk.CTkOptionMenu(self.theme_frame, values=["System", "Dark", "Light"], command=self._change_theme)
        self.theme_menu.pack(side="right", padx=10, pady=10)
        
        current_theme = self.db.get_setting("theme", "System")
        self.theme_menu.set(current_theme)

        # Watched Folders Setting
        self.folders_frame = ctk.CTkFrame(self)
        self.folders_frame.pack(fill="x", padx=20, pady=10)
        
        top_bar = ctk.CTkFrame(self.folders_frame, fg_color="transparent")
        top_bar.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(top_bar, text="Indexed Folders:").pack(side="left")
        self.btn_add_folder = ctk.CTkButton(top_bar, text="Add Folder", command=self._add_folder)
        self.btn_add_folder.pack(side="right")

        self.folders_list_frame = ctk.CTkScrollableFrame(self.folders_frame, height=150)
        self.folders_list_frame.pack(fill="x", padx=10, pady=(0, 10))

        self._load_folders()

    def _change_theme(self, new_theme: str):
        ctk.set_appearance_mode(new_theme)
        self.db.set_setting("theme", new_theme)

    def _load_folders(self):
        """Loads watched folders from settings."""
        # Clear current list
        for widget in self.folders_list_frame.winfo_children():
            widget.destroy()

        folders_str = self.db.get_setting("watched_folders", "")
        if folders_str:
            folders = folders_str.split(";")
            for folder in folders:
                if folder:
                    self._create_folder_item(folder)

    def _create_folder_item(self, folder_path: str):
        """Creates a UI row for a watched folder."""
        row = ctk.CTkFrame(self.folders_list_frame, fg_color="transparent")
        row.pack(fill="x", pady=2)
        
        lbl = ctk.CTkLabel(row, text=folder_path, anchor="w")
        lbl.pack(side="left", fill="x", expand=True, padx=5)
        
        btn_del = ctk.CTkButton(row, text="Remove", width=60, fg_color="#D32F2F", hover_color="#B71C1C",
                                command=lambda f=folder_path: self._remove_folder(f))
        btn_del.pack(side="right", padx=5)

    def _add_folder(self):
        folder_path = filedialog.askdirectory(title="Select Folder to Index")
        if folder_path:
            folders_str = self.db.get_setting("watched_folders", "")
            folders = folders_str.split(";") if folders_str else []
            
            if folder_path not in folders:
                folders.append(folder_path)
                self.db.set_setting("watched_folders", ";".join(folders))
                self._load_folders()
                self.on_folder_added(folder_path)

    def _remove_folder(self, folder_path: str):
        folders_str = self.db.get_setting("watched_folders", "")
        folders = folders_str.split(";") if folders_str else []
        
        if folder_path in folders:
            folders.remove(folder_path)
            self.db.set_setting("watched_folders", ";".join(folders))
            self._load_folders()
            self.on_folder_removed(folder_path)
