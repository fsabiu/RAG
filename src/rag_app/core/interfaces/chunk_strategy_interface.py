from abc import ABC, abstractmethod
from typing import List

class ChunkStrategyInterface(ABC):
    @abstractmethod
    def chunk_text(self, content: str) -> List[str]:
        pass
