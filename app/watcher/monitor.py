import os
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from app.watcher.indexer import Indexer
from app.utils.logger import logger
from app.utils.image_utils import is_valid_image

class ImageEventHandler(FileSystemEventHandler):
    def __init__(self, indexer: Indexer):
        self.indexer = indexer

    def on_created(self, event):
        """Triggered when a file or directory is created."""
        if not event.is_directory and is_valid_image(event.src_path):
            logger.info(f"New image detected: {event.src_path}")
            # Small delay to ensure the file is fully written before processing
            time.sleep(1) 
            self.indexer.add_to_queue(event.src_path)

class FolderMonitor:
    def __init__(self, indexer: Indexer):
        self.indexer = indexer
        self.observer = Observer()
        self.watches = {} # path -> watch object
        self.event_handler = ImageEventHandler(self.indexer)

    def start(self):
        """Starts the observer."""
        self.observer.start()
        logger.info("Folder monitor started.")

    def stop(self):
        """Stops the observer."""
        self.observer.stop()
        self.observer.join()
        logger.info("Folder monitor stopped.")

    def watch_folder(self, folder_path: str):
        """Adds a folder to watch list."""
        if not os.path.exists(folder_path):
            logger.error(f"Cannot watch non-existent folder: {folder_path}")
            return
            
        if folder_path not in self.watches:
            watch = self.observer.schedule(self.event_handler, folder_path, recursive=True)
            self.watches[folder_path] = watch
            logger.info(f"Now watching folder: {folder_path}")

    def unwatch_folder(self, folder_path: str):
        """Removes a folder from watch list."""
        if folder_path in self.watches:
            self.observer.unschedule(self.watches[folder_path])
            del self.watches[folder_path]
            logger.info(f"Stopped watching folder: {folder_path}")
