from typing import List
import logging
from src.rag_app.core.interfaces.chunk_strategy_interface import ChunkStrategyInterface

logger = logging.getLogger(__name__)

class FixedSizeChunkStrategy(ChunkStrategyInterface):
    def __init__(self, chunk_size: int, overlap: int = 0):
        self.chunk_size = chunk_size
        self.overlap = overlap

    def chunk_text(self, content: str) -> List[str]:
        logger.info(f"Applying fixed size chunking strategy with size {self.chunk_size} and overlap {self.overlap}")
        
        chunks = []
        start = 0
        content_length = len(content)

        while start < content_length:
            end = start + self.chunk_size
            chunk = content[start:end]
            chunks.append(chunk)
            
            start = end - self.overlap

        logger.info(f"Created {len(chunks)} chunks")
        return chunks
