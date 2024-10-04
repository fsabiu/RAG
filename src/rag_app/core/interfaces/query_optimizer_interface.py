from abc import ABC, abstractmethod

class QueryOptimizerInterface(ABC):
    @abstractmethod
    def optimize(self, query: str) -> str:
        pass
