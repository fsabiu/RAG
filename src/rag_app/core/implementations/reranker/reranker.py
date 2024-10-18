from typing import List, Dict, Any
import logging
from src.rag_app.core.interfaces.reranker_interface import ReRankerInterface

logger = logging.getLogger(__name__)

class ResultReRanker(ReRankerInterface):
    def re_rank(self, results: List[Dict[str, Any]], original_query: str) -> List[Dict[str, Any]]:
        logger.info(f"Re-ranking {len(results)} results for query: {original_query}")
        
        # Sort results by score in descending order
        re_ranked_results = sorted(results, key=lambda x: x['score'], reverse=True)
        
        return re_ranked_results
