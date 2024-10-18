from typing import List, Optional, Dict
from ...interfaces.document_interface import DocumentInterface, Chunk
import uuid

class PythonDocument(DocumentInterface):
    def __init__(self, id: str, name: str, collection: str, title: str, content: Optional[str] = None):
        self._id = id
        self._name = name
        self._collection = collection
        self._title = title
        self._content = content
        self._keywords: List[str] = []
        self._chunks: List[Chunk] = []

    @property
    def id(self) -> str:
        return self._id

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
    def content(self) -> Optional[str]:
        return self._content

    @content.setter
    def content(self, value: str) -> None:
        self._content = value

    @property
    def keywords(self) -> List[str]:
        return self._keywords

    @keywords.setter
    def keywords(self, value: List[str]) -> None:
        self._keywords = value

    @property
    def chunks(self) -> List[Chunk]:
        return self._chunks

    @chunks.setter
    def chunks(self, value: List[Chunk]) -> None:
        self._chunks = [Chunk(document_id=chunk.document_id, 
                              chunk_id=chunk.chunk_id, 
                              content=chunk.content, 
                              metadata={**chunk.metadata, 'document_name': self._name}) 
                        for chunk in value]

    def __repr__(self):
        return f"PythonDocument(id='{self.id}', name='{self.name}', collection='{self.collection}', title='{self.title}', keywords={len(self._keywords)}, chunks={len(self._chunks)})"
