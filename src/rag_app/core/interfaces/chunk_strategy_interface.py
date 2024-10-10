from abc import ABC, abstractmethod
from typing import List, Dict

class ChunkStrategyInterface(ABC):
    @property
    @abstractmethod
    def strategy_name(self) -> str:
        pass

    @abstractmethod
    def get_parameters(self) -> Dict[str, any]:
        pass

    @abstractmethod
    def chunk_text(self, content: str) -> List[str]:
        pass
