from abc import ABC, abstractmethod
from typing import List, Protocol

class DocumentInterface(ABC):
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
    def content(self) -> str:
        pass

    @abstractmethod
    def get_keywords(self) -> List[str]:
        pass

    @abstractmethod
    def set_keywords(self, keywords: List[str]) -> None:
        pass

    @abstractmethod
    def get_chunks(self) -> List[str]:
        pass

    @abstractmethod
    def set_chunks(self, chunks: List[str]) -> None:
        pass

class DocumentFactoryInterface(Protocol):
    def create_document(self, name: str, collection: str, title: str, content: str) -> DocumentInterface:
        ...
