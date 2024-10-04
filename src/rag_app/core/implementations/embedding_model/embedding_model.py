from typing import List
import logging
import os
import cohere
import numpy as np
from ...interfaces.embedding_model_interface import EmbeddingModelInterface

logger = logging.getLogger(__name__)

class CohereEmbedding(EmbeddingModelInterface):
    def __init__(self, model_name: str = "embed-english-v3.0"):
        self.model_name = model_name
        api_key = os.environ.get("COHERE_API_KEY")
        if not api_key:
            raise ValueError("COHERE_API_KEY environment variable is not set")
        self.client = cohere.ClientV2(api_key=api_key)
        logger.info(f"Initializing Cohere embedding model: {model_name}")

    def generate_embedding(self, chunk: str) -> List[float]:
        logger.debug(f"Generating embedding for chunk: {chunk[:50]}...")
        res = self.client.embed(
            texts=[chunk],
            model=self.model_name,
            input_type="search_query",
            embedding_types=['float']
        )
        return res.embeddings.float[0]

    @staticmethod
    def calculate_similarity(a: List[float], b: List[float]) -> float:
        return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))
