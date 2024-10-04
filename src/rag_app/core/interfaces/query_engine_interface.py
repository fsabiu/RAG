from abc import ABC, abstractmethod
from typing import Dict, Any

class QueryEngineInterface(ABC):
    @abstractmethod
    def prepare_domains(self) -> None:
        pass

    @abstractmethod
    def ask_question(self, question: str, domain_name: str) -> Dict[str, Any]:
        pass
