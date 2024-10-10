from typing import List, Dict
import logging
from src.rag_app.core.interfaces.chunk_strategy_interface import ChunkStrategyInterface

logger = logging.getLogger(__name__)

class FixedSizeChunkStrategy(ChunkStrategyInterface):
    def __init__(self, chunk_size: int, overlap: int = 0):
        self._strategy_name = "Fixed Size"
        self.chunk_size = chunk_size
        self.overlap = overlap

    @property
    def strategy_name(self) -> str:
        return self._strategy_name

    def get_parameters(self) -> Dict[str, any]:
        return {
            "chunk_size": self.chunk_size,
            "overlap": self.overlap
        }

    def chunk_text(self, content: str) -> List[str]:
        if content is None:
            print("Warning: Received None content in chunk_text method")
            return []  # or handle this case appropriately
        
        chunks = []
        start = 0
        content_length = len(content)

        while start < content_length:
            end = start + self.chunk_size
            chunk = content[start:end]
            chunks.append(chunk)
            
            start = end - self.overlap
            
        return chunks
