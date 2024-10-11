from abc import ABC, abstractmethod
from typing import List, Union
import numpy as np

class EmbeddingModelInterface(ABC):
    @property
    @abstractmethod
    def model_name(self) -> str:
        pass

    @abstractmethod
    def generate_embedding(self, chunks: Union[str, List[str]]) -> Union[List[float], List[List[float]]]:
        pass

    @staticmethod
    def calculate_cosine_similarity(a: List[float], b: List[float]) -> float:
        return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

    @staticmethod
    def calculate_l2_similarity(a: List[float], b: List[float]) -> float:
        distance = np.linalg.norm(np.array(a) - np.array(b))
        return 1 / (1 + distance)  # Convert distance to similarity

    @staticmethod
    def calculate_dot_product_similarity(a: List[float], b: List[float]) -> float:
        return np.dot(a, b)