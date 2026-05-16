from typing import List, Dict, Any
from thefuzz import fuzz

from app.database.db_manager import DatabaseManager
from app.utils.logger import logger

class SearchEngine:
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager

    def search(self, query: str, fuzzy_threshold: int = 60) -> List[Dict[str, Any]]:
        """
        Searches screenshots for the given query.
        Implements ranking based on exact match and fuzzy matching.
        """
        if not query or query.strip() == "":
            return []
            
        query = query.strip().lower()
        logger.info(f"Searching for: {query}")
        
        # Log search history
        self._log_search(query)

        # 1. Get initial candidate list from DB
        # If the query is very short, we might want to get all and fuzzy search
        # or do a broad LIKE query
        candidates = self.db.search_screenshots(query)
        
        # If no strict exact matches, retrieve a broader set to apply fuzzy matching
        # (For offline large DBs, retrieving all might be slow, so we can limit this in production, 
        # but for a personal screenshot tool, retrieving 1000s of rows is usually fast enough)
        if not candidates:
             candidates = self.db.get_all_screenshots()

        scored_results = []
        for row in candidates:
            score = self._calculate_score(query, row)
            if score >= fuzzy_threshold:
                # Add score to row data for sorting
                row_data = dict(row)
                row_data['score'] = score
                scored_results.append(row_data)

        # Sort by score descending, then by date descending
        scored_results.sort(key=lambda x: (x['score'], x['created_date']), reverse=True)
        
        return scored_results

    def _calculate_score(self, query: str, row: Dict[str, Any]) -> int:
        """Calculates a relevance score for a row against the query."""
        score = 0
        filename = row.get('filename', '').lower()
        ocr_text = row.get('ocr_text', '').lower()
        
        # 1. Exact Match bonuses
        if query in filename:
            score = max(score, 100) # Filename match is strong
        if query in ocr_text:
            score = max(score, 95)  # Exact text match is also strong

        # 2. Fuzzy Matching
        if score < 95:
            # We use token_set_ratio because text might be scattered
            fuzzy_text_score = fuzz.token_set_ratio(query, ocr_text)
            fuzzy_file_score = fuzz.partial_ratio(query, filename)
            
            # Combine or take the max
            score = max(score, fuzzy_text_score, fuzzy_file_score)
            
        return score

    def _log_search(self, query: str):
        """Logs the search query to history."""
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('INSERT INTO search_history (query) VALUES (?)', (query,))
                conn.commit()
        except Exception as e:
            logger.error(f"Failed to log search history: {e}")

    def get_recent_searches(self, limit: int = 10) -> List[str]:
        """Retrieves recent search queries."""
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT DISTINCT query FROM search_history ORDER BY timestamp DESC LIMIT ?', (limit,))
                return [row['query'] for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Failed to get recent searches: {e}")
            return []
