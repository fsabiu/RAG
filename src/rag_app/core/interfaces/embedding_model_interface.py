from abc import ABC, abstractmethod
from typing import List

class EmbeddingModelInterface(ABC):
    @abstractmethod
    def generate_embedding(self, chunk: str) -> List[float]:
        pass

    @staticmethod
    @abstractmethod
    def calculate_similarity(a: List[float], b: List[float]) -> float:
        pass
