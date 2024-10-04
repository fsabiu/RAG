from abc import ABC, abstractmethod
from typing import Dict, List
from .domain_interface import DomainInterface

class DomainManagerInterface(ABC):
    @abstractmethod
    def get_domains(self) -> List[DomainInterface]:
        pass

    @abstractmethod
    def get_domain(self, domain_name: str) -> DomainInterface:
        pass

    @abstractmethod
    def apply_chunking_strategy(self) -> None:
        pass
