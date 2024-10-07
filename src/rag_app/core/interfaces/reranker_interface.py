from abc import ABC, abstractmethod
from typing import List, Dict, Any

class ReRankerInterface(ABC):
    @abstractmethod
    def re_rank(self, results: List[Dict[str, Any]], original_query: str) -> List[Dict[str, Any]]:
        """
        Re-rank the given results based on the original query.

        Args:
            results (List[Dict[str, Any]]): The initial list of results to be re-ranked.
            original_query (str): The original query used to obtain the results.

        Returns:
            List[Dict[str, Any]]: The re-ranked list of results.
        """
        pass
