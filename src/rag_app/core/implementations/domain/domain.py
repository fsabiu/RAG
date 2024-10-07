from typing import List
from ...interfaces.document_interface import DocumentInterface
from ...interfaces.domain_interface import DomainInterface

class Domain(DomainInterface):
    def __init__(self, name: str, description: str, documents: List[DocumentInterface]):
        self.name = name
        self.description = description
        self.documents = documents

    def __repr__(self):
        return f"Domain(name='{self.name}', description='{self.description}', documents={len(self.documents)})"
