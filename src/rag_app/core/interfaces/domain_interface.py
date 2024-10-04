from typing import List, Protocol
from ..implementations.document import Document

class DomainInterface(Protocol):
    name: str
    description: str
    documents: List[Document]

    def __repr__(self) -> str:
        ...
