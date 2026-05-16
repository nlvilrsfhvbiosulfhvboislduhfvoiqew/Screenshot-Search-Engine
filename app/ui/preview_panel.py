import os
import customtkinter as ctk
from PIL import Image

class PreviewPanel(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        
        self.current_image_path = None
        self.current_ocr_text = ""

        # Title Label
        self.title_label = ctk.CTkLabel(self, text="Preview", font=ctk.CTkFont(size=16, weight="bold"))
        self.title_label.pack(pady=10, padx=10, anchor="w")

        # Image Container
        self.image_label = ctk.CTkLabel(self, text="No image selected")
        self.image_label.pack(pady=10, padx=10, fill="both", expand=True)

        # OCR Text Area
        self.text_area_label = ctk.CTkLabel(self, text="Extracted Text:", font=ctk.CTkFont(weight="bold"))
        self.text_area_label.pack(pady=(10, 0), padx=10, anchor="w")

        self.text_area = ctk.CTkTextbox(self, height=150)
        self.text_area.pack(pady=5, padx=10, fill="x")

        # Actions
        self.btn_copy = ctk.CTkButton(self, text="Copy Text", command=self._copy_text)
        self.btn_copy.pack(pady=10, padx=10, anchor="e")

    def load_image(self, path: str, ocr_text: str):
        """Loads an image into the preview panel."""
        self.current_image_path = path
        self.current_ocr_text = ocr_text
        
        try:
            # Display image
            pil_image = Image.open(path)
            # Resize for preview maintaining aspect ratio
            # Let's target a max width/height based on common screen sizes
            pil_image.thumbnail((400, 400))
            ctk_image = ctk.CTkImage(light_image=pil_image, dark_image=pil_image, size=pil_image.size)
            self.image_label.configure(image=ctk_image, text="")
            
            # Display text
            self.text_area.delete("1.0", ctk.END)
            self.text_area.insert("1.0", ocr_text if ocr_text else "No text found.")
            
        except Exception as e:
            self.image_label.configure(image=None, text=f"Error loading image:\n{e}")
            self.text_area.delete("1.0", ctk.END)

    def clear(self):
        """Clears the preview panel."""
        self.current_image_path = None
        self.current_ocr_text = ""
        self.image_label.configure(image=None, text="No image selected")
        self.text_area.delete("1.0", ctk.END)

    def _copy_text(self):
        """Copies OCR text to clipboard."""
        if self.current_ocr_text:
            self.master.clipboard_clear()
            self.master.clipboard_append(self.current_ocr_text)
            
            # Visual feedback
            original_text = self.btn_copy.cget("text")
            self.btn_copy.configure(text="Copied!")
            self.after(2000, lambda: self.btn_copy.configure(text=original_text))
