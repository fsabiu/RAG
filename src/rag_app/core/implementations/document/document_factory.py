from typing import Optional, Literal
from ...interfaces.document_interface import DocumentFactoryInterface, DocumentInterface
from .py_document import PythonDocument
from .db_document import DBDocument

# Define a type for the implementation parameter
ImplementationType = Literal["OCI_DB", "Python"]

class DocumentFactory(DocumentFactoryInterface):
    def __init__(self, implementation: ImplementationType = "Python", db_connection=None):
        self.implementation = implementation
        self.db_connection = db_connection

    def create_document(self, id: str, name: str, collection: str, title: str, content: Optional[str] = None) -> DocumentInterface:
        if self.implementation == "OCI_DB":
            if not self.db_connection:
                raise ValueError("Database connection is required for OCI_DB implementation")
            return DBDocument(id, name, collection, title, content, self.db_connection)
        elif self.implementation == "Python":
            return PythonDocument(id, name, collection, title, content)
        else:
            raise ValueError(f"Invalid implementation: {self.implementation}. Must be either 'OCI_DB' or 'Python'")
