from abc import ABC, abstractmethod
from typing import List, Dict, Any

class VectorStoreInterface(ABC):
    @abstractmethod
    def store_embeddings(self, embeddings: List[List[float]], metadata: List[Dict[str, Any]], ids: List[str], documents: List[str]) -> None:
        pass

    @abstractmethod
    def query(self, query_embedding: List[float], top_k: int = 10) -> List[Dict[str, Any]]:
        pass
