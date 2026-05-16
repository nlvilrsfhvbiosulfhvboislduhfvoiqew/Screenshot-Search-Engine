import os
import sys

# Ensure the app directory is in the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database.db_manager import DatabaseManager
from app.ocr.engine import OCREngine
from app.search.engine import SearchEngine
from app.watcher.indexer import Indexer
from app.watcher.monitor import FolderMonitor
from app.ui.main_window import MainWindow
from app.utils.logger import logger

class ApplicationController:
    def __init__(self):
        logger.info("Initializing Screenshot Search Engine...")
        
        # 1. Initialize DB
        self.db_manager = DatabaseManager()
        
        # 2. Initialize OCR Engine
        self.ocr_engine = OCREngine()
        
        # 3. Initialize Search Engine
        self.search_engine = SearchEngine(self.db_manager)
        
        # 4. Initialize Background Indexer
        self.indexer = Indexer(self.db_manager, self.ocr_engine)
        
        # 5. Initialize Folder Monitor
        self.folder_monitor = FolderMonitor(self.indexer)
        
        # 6. Initialize UI
        self.ui = MainWindow(
            db_manager=self.db_manager,
            search_engine=self.search_engine,
            on_folder_added=self.handle_folder_added,
            on_folder_removed=self.handle_folder_removed,
            on_force_reindex=self.handle_force_reindex
        )
        
        # Connect Indexer to UI updates
        self.indexer.register_callback(self.ui.notify_new_image)

    def start(self):
        """Starts the application and background services."""
        logger.info("Starting background services...")
        
        # Start Indexer Thread
        self.indexer.start()
        
        # Load watched folders and start monitoring
        self._start_monitoring_saved_folders()
        
        # Start UI loop (blocks until closed)
        logger.info("Starting UI loop...")
        self.ui.mainloop()
        
        # Cleanup on exit
        self._shutdown()

    def _start_monitoring_saved_folders(self):
        """Starts monitoring folders saved in settings."""
        folders_str = self.db_manager.get_setting("watched_folders", "")
        if folders_str:
            folders = folders_str.split(";")
            
            # Start the monitor
            self.folder_monitor.start()
            
            for folder in folders:
                if folder and os.path.exists(folder):
                    self.folder_monitor.watch_folder(folder)

    def handle_folder_added(self, folder_path: str):
        """Callback when user adds a folder from UI."""
        logger.info(f"User added folder to watch: {folder_path}")
        
        # Ensure monitor is running
        try:
            if not self.folder_monitor.observer.is_alive():
                self.folder_monitor.start()
        except RuntimeError:
             # Observer might be stopped and cannot be restarted, create new if needed
             # (In this simple app structure we only start it once)
             pass
             
        self.folder_monitor.watch_folder(folder_path)
        # Immediately queue all files in the new folder
        self.indexer.scan_directory(folder_path)

    def handle_folder_removed(self, folder_path: str):
        """Callback when user removes a folder from UI."""
        logger.info(f"User removed folder from watch: {folder_path}")
        self.folder_monitor.unwatch_folder(folder_path)

    def handle_force_reindex(self):
        """Forces a re-scan of all watched folders."""
        logger.info("Force re-index initiated by user.")
        folders_str = self.db_manager.get_setting("watched_folders", "")
        if folders_str:
            folders = folders_str.split(";")
            for folder in folders:
                if folder and os.path.exists(folder):
                    self.indexer.scan_directory(folder)

    def _shutdown(self):
        """Cleanly shuts down background threads."""
        logger.info("Shutting down Application Controller...")
        self.indexer.stop()
        try:
            self.folder_monitor.stop()
        except Exception:
            pass

if __name__ == "__main__":
    app = ApplicationController()
    app.start()
