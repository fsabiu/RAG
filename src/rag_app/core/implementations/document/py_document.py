from typing import List, Optional
from ...interfaces.document_interface import DocumentInterface

class PythonDocument(DocumentInterface):
    def __init__(self, name: str, collection: str, title: str, content: Optional[str] = None):
        self._name = name
        self._collection = collection
        self._title = title
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

    def get_content(self) -> Optional[str]:
        return self._content

    def set_content(self, content: str) -> None:
        self._content = content

    def get_keywords(self) -> List[str]:
        return self._keywords

    def set_keywords(self, keywords: List[str]) -> None:
        self._keywords = keywords

    def get_chunks(self) -> List[str]:
        return self._chunks

    def set_chunks(self, chunks: List[str]) -> None:
        self._chunks = chunks

    def __repr__(self):
        return f"PythonDocument(name='{self.name}', collection='{self.collection}', title='{self.title}', keywords={len(self._keywords)}, chunks={len(self._chunks)})"
