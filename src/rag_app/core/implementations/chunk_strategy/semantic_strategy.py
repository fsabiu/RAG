from typing import List, Dict
import logging
from src.rag_app.core.interfaces.chunk_strategy_interface import ChunkStrategyInterface
from src.rag_app.core.interfaces.embedding_model_interface import EmbeddingModelInterface

logger = logging.getLogger(__name__)

class SemanticChunkStrategy(ChunkStrategyInterface):
    def __init__(self, embedding_model: EmbeddingModelInterface, max_chunk_size: int = 1024):
        self._strategy_name = "Semantic"
        self.embedding_model = embedding_model
        self.max_chunk_size = max_chunk_size  # Add max_chunk_size parameter

    @property
    def strategy_name(self) -> str:
        return self._strategy_name

    def get_parameters(self) -> Dict[str, any]:
        return {
            "embedding_model": str(self.embedding_model.model_name),
            "max_chunk_size": self.max_chunk_size  # Include max_chunk_size in parameters
        }

    def chunk_text(self, content: str) -> List[str]:
        logger.info("Applying semantic chunking strategy")
        
        # Step 2: Separate the sentences
        sentences = content.split('. ')  # Simple sentence splitting, can be improved
        
        # Step 3: Generate embeddings for each sentence
        embeddings = [self.embedding_model.generate_embedding(sentence) for sentence in sentences]
        
        # Step 4: Calculate similarity scores
        similarities = [
            self.embedding_model.calculate_similarity(embeddings[i], embeddings[i - 1])
            for i in range(1, len(embeddings))
        ]
        
        # Step 5: Splitting into chunks recursively
        def recursive_split(start_idx, end_idx):
            if start_idx >= end_idx:
                return []
            
            # Calculate chunk size
            chunk = '. '.join(sentences[start_idx:end_idx + 1])
            if len(chunk) <= self.max_chunk_size:
                return [chunk]
            
            # Find the index with the lowest similarity
            min_similarity_idx = start_idx + similarities[start_idx:end_idx].index(min(similarities[start_idx:end_idx]))
            
            # Recursively split the text
            return recursive_split(start_idx, min_similarity_idx) + recursive_split(min_similarity_idx + 1, end_idx)
        
        # Call the recursive function to start the process
        return recursive_split(0, len(sentences) - 1)