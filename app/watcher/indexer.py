import os
import queue
import threading
import time

from app.database.db_manager import DatabaseManager
from app.ocr.engine import OCREngine
from app.utils.image_utils import get_image_hash, create_thumbnail, is_valid_image
from app.utils.logger import logger

class Indexer:
    def __init__(self, db_manager: DatabaseManager, ocr_engine: OCREngine):
        self.db = db_manager
        self.ocr = ocr_engine
        self.queue = queue.Queue()
        self.is_running = False
        self.thread = None
        self.callbacks = [] # UI update callbacks

    def start(self):
        """Starts the background indexing thread."""
        if not self.is_running:
            self.is_running = True
            self.thread = threading.Thread(target=self._worker_loop, daemon=True)
            self.thread.start()
            logger.info("Indexer thread started.")

    def stop(self):
        """Stops the indexing thread."""
        self.is_running = False
        if self.thread:
            # We don't join here to avoid blocking UI, daemon thread will die anyway
            logger.info("Indexer thread stopping.")

    def add_to_queue(self, file_path: str):
        """Adds a file to the indexing queue."""
        if is_valid_image(file_path):
            self.queue.put(file_path)

    def scan_directory(self, dir_path: str):
        """Recursively scans a directory and adds images to the queue."""
        if not os.path.exists(dir_path):
            logger.error(f"Directory does not exist: {dir_path}")
            return

        logger.info(f"Scanning directory: {dir_path}")
        for root, _, files in os.walk(dir_path):
            for file in files:
                file_path = os.path.join(root, file)
                if is_valid_image(file_path):
                    self.add_to_queue(file_path)

    def _worker_loop(self):
        """Background worker loop to process images from the queue."""
        while self.is_running:
            try:
                # Use timeout to allow checking is_running flag
                file_path = self.queue.get(timeout=1.0)
                self._process_image(file_path)
                self.queue.task_done()
            except queue.Empty:
                continue
            except Exception as e:
                logger.error(f"Error in indexer worker loop: {e}")

    def _process_image(self, file_path: str):
        """Processes a single image: hash, thumbnail, OCR, DB insert."""
        try:
            # 1. Generate Phash and check for duplicates
            phash = get_image_hash(file_path)
            
            # Simple deduplication strategy: if exact hash exists, we might skip OCR 
            # but we still want to record the new path if it's different.
            # In this simple implementation, if the path is same, it ignores.
            
            # 2. Extract OCR text
            ocr_text = self.ocr.extract_text(file_path)
            
            # 3. Generate Thumbnail
            thumbnail_path = create_thumbnail(file_path)
            
            # 4. Save to Database
            filename = os.path.basename(file_path)
            self.db.insert_screenshot(
                path=file_path, 
                filename=filename, 
                ocr_text=ocr_text, 
                phash=phash, 
                thumbnail_path=thumbnail_path
            )
            
            # 5. Notify UI
            for callback in self.callbacks:
                try:
                    callback(file_path)
                except Exception as e:
                    logger.error(f"Error in indexer callback: {e}")
                    
            logger.info(f"Indexed: {file_path}")
            
        except Exception as e:
            logger.error(f"Failed to process image {file_path}: {e}")

    def register_callback(self, callback_func):
        """Registers a function to be called when an image is successfully indexed."""
        self.callbacks.append(callback_func)
