from typing import List, Union
import logging
import os
import cohere
import numpy as np
from ...interfaces.embedding_model_interface import EmbeddingModelInterface

logger = logging.getLogger(__name__)

class CohereEmbedding(EmbeddingModelInterface):
    def __init__(self, model_name: str = "embed-english-v3.0"):
        self._model_name = model_name
        api_key = os.environ.get("COHERE_API_KEY")
        if not api_key:
            raise ValueError("COHERE_API_KEY environment variable is not set")
        self.client = cohere.ClientV2(api_key=api_key)
        
        logger.info(f"Initializing Cohere embedding model: {model_name}")
        pass

    @property
    def model_name(self) -> str:
        return self._model_name

    def generate_embedding(self, chunks: Union[str, List[str]]) -> Union[List[float], List[List[float]]]:
        if isinstance(chunks, str):
            chunks = [chunks]
        
        logger.debug(f"Generating embeddings for {len(chunks)} chunk(s)")
        
        # Process chunks in batches of 96
        batch_size = 96
        all_embeddings = []
        
        for i in range(0, len(chunks), batch_size):
            batch = chunks[i:i+batch_size]
            logger.debug(f"Processing batch {i//batch_size + 1} with {len(batch)} chunks")
            
            res = self.client.embed(
                texts=batch,
                model=self.model_name,
                input_type="search_query",
                embedding_types=['float']
            )
            
            all_embeddings.extend(res.embeddings.float)
        
        return all_embeddings[0] if len(all_embeddings) == 1 else all_embeddings
