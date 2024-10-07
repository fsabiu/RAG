from ...interfaces.document_interface import DocumentFactoryInterface, DocumentInterface
from .document import Document

class DocumentFactory(DocumentFactoryInterface):
    def create_document(self, name: str, collection: str, title: str, content: str) -> DocumentInterface:
        return Document(name, collection, content)
