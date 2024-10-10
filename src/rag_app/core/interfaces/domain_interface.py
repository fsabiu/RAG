from typing import List, Protocol
from .document_interface import DocumentInterface

class DomainInterface(Protocol):
    @property
    def name(self) -> str:
        ...

    @property
    def description(self) -> str:
        ...

    @description.setter
    def description(self, value: str):
        ...

    @property
    def documents(self) -> List[DocumentInterface]:
        ...

    @documents.setter
    def documents(self, value: List[DocumentInterface]):
        ...

    def __repr__(self) -> str:
        ...

class DomainFactoryInterface(Protocol):
    def create_domain(self, name: str, description: str, documents: List[DocumentInterface]) -> DomainInterface:
        ...
