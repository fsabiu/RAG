from typing import List, Dict
import logging
from src.rag_app.core.interfaces.chunk_strategy_interface import ChunkStrategyInterface
from src.rag_app.core.interfaces.document_interface import Chunk

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

    def chunk_text(self, content: str, document_id: str) -> List[Chunk]:
        if content is None:
            logger.warning("Received None content in chunk_text method")
            return []
        
        chunks = []
        start = 0
        content_length = len(content)
        chunk_id = 0

        while start < content_length:
            end = start + self.chunk_size
            chunk_content = content[start:end]
            chunk = Chunk(
                document_id=document_id,
                chunk_id=f"{document_id}_chunk_{chunk_id}",
                metadata={"start": start, "end": end},
                content=chunk_content
            )
            chunks.append(chunk)
            
            start = end - self.overlap
            chunk_id += 1
            
        return chunks
