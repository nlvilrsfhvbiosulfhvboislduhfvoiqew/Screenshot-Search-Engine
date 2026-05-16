import os
import customtkinter as ctk
from PIL import Image
from typing import List, Dict, Any, Callable

class ThumbnailCard(ctk.CTkFrame):
    def __init__(self, master, data: Dict[str, Any], on_click: Callable[[Dict[str, Any]], None], **kwargs):
        super().__init__(master, corner_radius=8, fg_color=("gray90", "gray13"), **kwargs)
        self.data = data
        self.on_click = on_click
        
        self.bind("<Button-1>", self._on_click_handler)

        # Load Thumbnail
        thumb_path = data.get('thumbnail_path')
        if thumb_path and os.path.exists(thumb_path):
            try:
                pil_image = Image.open(thumb_path)
                self.ctk_image = ctk.CTkImage(light_image=pil_image, dark_image=pil_image, size=(120, 120))
                self.img_label = ctk.CTkLabel(self, image=self.ctk_image, text="")
            except Exception:
                self.img_label = ctk.CTkLabel(self, text="Error")
        else:
            self.img_label = ctk.CTkLabel(self, text="No Thumb")
            
        self.img_label.pack(pady=(10, 5), padx=10)
        self.img_label.bind("<Button-1>", self._on_click_handler)

        # Title Label
        filename = data.get('filename', 'Unknown')
        if len(filename) > 15:
            filename = filename[:12] + "..."
        self.title_label = ctk.CTkLabel(self, text=filename, font=ctk.CTkFont(size=11))
        self.title_label.pack(pady=(0, 5), padx=10)
        self.title_label.bind("<Button-1>", self._on_click_handler)

        # Hover effects
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        self.img_label.bind("<Enter>", self._on_enter)
        self.img_label.bind("<Leave>", self._on_leave)

    def _on_click_handler(self, event):
        self.on_click(self.data)

    def _on_enter(self, event):
        self.configure(fg_color=("gray80", "gray20"))

    def _on_leave(self, event):
        self.configure(fg_color=("gray90", "gray13"))


class ImageGrid(ctk.CTkScrollableFrame):
    def __init__(self, master, on_image_click: Callable[[Dict[str, Any]], None], **kwargs):
        super().__init__(master, **kwargs)
        self.on_image_click = on_image_click
        self.cards = []
        
        # Grid settings
        self.columns = 3
        self.current_row = 0
        self.current_col = 0

    def update_results(self, results: List[Dict[str, Any]]):
        """Clears the grid and populates it with new results."""
        # Clear existing
        for widget in self.winfo_children():
            widget.destroy()
        self.cards.clear()
        
        self.current_row = 0
        self.current_col = 0

        if not results:
            lbl = ctk.CTkLabel(self, text="No screenshots found.", font=ctk.CTkFont(size=14))
            lbl.grid(row=0, column=0, padx=20, pady=20)
            return

        # Let's dynamically adjust columns based on width later, for now fix at 3
        # Or better, let grid wrap
        for item in results:
            card = ThumbnailCard(self, item, self.on_image_click)
            card.grid(row=self.current_row, column=self.current_col, padx=10, pady=10, sticky="nsew")
            self.cards.append(card)
            
            self.current_col += 1
            if self.current_col >= self.columns:
                self.current_col = 0
                self.current_row += 1
