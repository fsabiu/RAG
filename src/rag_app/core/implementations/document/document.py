from typing import List
from ...interfaces.document_interface import DocumentInterface

class Document(DocumentInterface):
    def __init__(self, name: str, collection: str, content: str):
        self._name = name
        self._collection = collection
        self._title = name  # Same as name for now
        self._content = content
        self._keywords: List[str] = []
        self._chunks: List[str] = []

    @property
    def name(self) -> str:
        return self._name

    @property
    def collection(self) -> str:
        return self._collection

    @property
    def title(self) -> str:
        return self._title

    @property
    def content(self) -> str:
        return self._content

    def get_keywords(self) -> List[str]:
        return self._keywords

    def set_keywords(self, keywords: List[str]) -> None:
        self._keywords = keywords

    def get_chunks(self) -> List[str]:
        return self._chunks

    def set_chunks(self, chunks: List[str]) -> None:
        self._chunks = chunks

    def __repr__(self):
        return f"Document(name='{self.name}', collection='{self.collection}', title='{self.title}', keywords={len(self._keywords)}, chunks={len(self._chunks)})"
