from typing import List
from ...interfaces.document_interface import DocumentInterface
from ...interfaces.domain_interface import DomainInterface

class Domain(DomainInterface):
    def __init__(self, name: str, description: str, documents: List[DocumentInterface]):
        self._name = name
        self._description = description
        self._documents = documents

    @property
    def name(self) -> str:
        return self._name

    @property
    def description(self) -> str:
        return self._description

    @description.setter
    def description(self, value: str):
        self._description = value

    @property
    def documents(self) -> List[DocumentInterface]:
        return self._documents

    @documents.setter
    def documents(self, value: List[DocumentInterface]):
        self._documents = value

    def __repr__(self):
        return f"Domain(name='{self._name}', description='{self._description}', documents={len(self._documents)})"
