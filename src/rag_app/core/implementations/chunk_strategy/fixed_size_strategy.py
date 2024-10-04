from typing import List
import logging
from src.rag_app.core.interfaces.chunk_strategy import ChunkStrategy

logger = logging.getLogger(__name__)

class FixedSizeChunkStrategy(ChunkStrategy):
    def __init__(self, chunk_size: int, overlap: int = 0):
        self.chunk_size = chunk_size
        self.overlap = overlap

    def chunk_text(self, content: str) -> List[str]:
        logger.info(f"Applying fixed size chunking strategy with size {self.chunk_size} and overlap {self.overlap}")
        # Implement fixed size chunking logic here
        return [content]
