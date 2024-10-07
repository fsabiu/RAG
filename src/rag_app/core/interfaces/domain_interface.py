from typing import List, Protocol
from .document_interface import DocumentInterface

class DomainInterface(Protocol):
    name: str
    description: str
    documents: List[DocumentInterface]

    def __repr__(self) -> str:
        ...

class DomainFactoryInterface(Protocol):
    def create_domain(self, name: str, description: str, documents: List[DocumentInterface]) -> DomainInterface:
        ...
