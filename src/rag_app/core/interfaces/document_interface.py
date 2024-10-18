from abc import ABC, abstractmethod
from typing import List, Protocol, Optional, Dict, Any

class Chunk:
    def __init__(self, document_id: str, chunk_id: str, content: str, metadata: Dict[str, Any]):
        self._content = content
        self._document_id = document_id
        self._metadata = metadata
        self._chunk_id = chunk_id

    @property
    def content(self) -> str:
        return self._content

    @property
    def document_id(self) -> str:
        return self._document_id

    @property
    def metadata(self) -> Dict[str, Any]:
        return self._metadata

    @property
    def chunk_id(self) -> str:
        return self._chunk_id

class DocumentInterface(ABC):
    @property
    @abstractmethod
    def id(self) -> str:
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @property
    @abstractmethod
    def collection(self) -> str:
        pass

    @property
    @abstractmethod
    def title(self) -> str:
        pass

    @property
    @abstractmethod
    def content(self) -> Optional[str]:
        pass

    @content.setter
    @abstractmethod
    def content(self, value: str) -> None:
        pass

    @property
    @abstractmethod
    def keywords(self) -> List[str]:
        pass

    @keywords.setter
    @abstractmethod
    def keywords(self, value: List[str]) -> None:
        pass

    @property
    @abstractmethod
    def chunks(self) -> List[Chunk]:
        pass

    @chunks.setter
    @abstractmethod
    def chunks(self, value: List[Chunk]) -> None:
        pass

    @property
    @abstractmethod
    def id(self) -> str:
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        pass

class DocumentFactoryInterface(Protocol):
    def create_document(self, name: str, collection: str, title: str, content: Optional[str] = None) -> DocumentInterface:
        ...
