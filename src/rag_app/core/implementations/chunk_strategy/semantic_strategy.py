from typing import List, Dict
import logging
from src.rag_app.core.interfaces.chunk_strategy_interface import ChunkStrategyInterface
from src.rag_app.core.interfaces.embedding_model_interface import EmbeddingModelInterface
from src.rag_app.core.interfaces.document_interface import Chunk

logger = logging.getLogger(__name__)

class SemanticChunkStrategy(ChunkStrategyInterface):
    def __init__(self, embedding_model: EmbeddingModelInterface, max_chunk_size: int = 1024):
        self._strategy_name = "Semantic"
        self.embedding_model = embedding_model
        self.max_chunk_size = max_chunk_size

    @property
    def strategy_name(self) -> str:
        return self._strategy_name

    def get_parameters(self) -> Dict[str, any]:
        return {
            "embedding_model": str(self.embedding_model.model_name),
            "max_chunk_size": self.max_chunk_size
        }

    def chunk_text(self, content: str, document_id: str) -> List[Chunk]:
        logger.info("Applying semantic chunking strategy")
        
        sentences = content.split('. ')
        embeddings = [self.embedding_model.generate_embedding(sentence) for sentence in sentences]
        similarities = [
            self.embedding_model.calculate_cosine_similarity(embeddings[i], embeddings[i - 1])
            for i in range(1, len(embeddings))
        ]
        
        def recursive_split(start_idx, end_idx, chunk_id):
            if start_idx >= end_idx:
                return []
            
            chunk_content = '. '.join(sentences[start_idx:end_idx + 1])
            if len(chunk_content) <= self.max_chunk_size:
                return [Chunk(
                    document_id=document_id,
                    chunk_id=f"{document_id}_chunk_{chunk_id}",
                    metadata={"start_sentence": start_idx, "end_sentence": end_idx},
                    content=chunk_content
                )]
            
            min_similarity_idx = start_idx + similarities[start_idx:end_idx].index(min(similarities[start_idx:end_idx]))
            
            return (recursive_split(start_idx, min_similarity_idx, chunk_id) +
                    recursive_split(min_similarity_idx + 1, end_idx, chunk_id + 1))
        
        return recursive_split(0, len(sentences) - 1, 0)