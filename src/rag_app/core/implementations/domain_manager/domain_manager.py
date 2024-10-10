import logging
from typing import Dict, List
from ...interfaces.domain_manager_interface import DomainManagerInterface
from ...interfaces.domain_interface import DomainInterface
from ...interfaces.document_interface import DocumentInterface
from ...interfaces.storage_interface import StorageInterface
from ...interfaces.chunk_strategy_interface import ChunkStrategyInterface
from ...interfaces.chat_model_interface import ChatModelInterface
from ..document.document import Document
from ..domain.domain import Domain

logger = logging.getLogger(__name__)

class DomainManager(DomainManagerInterface):
    def __init__(self, storage, chunk_strategy, chat_model, domain_factory, document_factory):
        self.storage = storage
        self.chunk_strategy = chunk_strategy
        self.chat_model = chat_model
        self.domain_factory = domain_factory
        self.document_factory = document_factory
        self.domains: Dict[str, DomainInterface] = self._create_domains()

    def _create_domains(self) -> Dict[str, DomainInterface]:
        domains = {}
        domain_names = self.storage.get_all_collections()  # Renamed variable for clarity
        
        for domain_name in domain_names:
            documents = self._create_documents(domain_name)
            description = self._get_domain_description(domain_name)  # Renamed method
            domains[domain_name] = self.domain_factory.create_domain(domain_name, description, documents)
        
        return domains

    def _create_documents(self, domain_name: str) -> List[DocumentInterface]:
        documents = []
        for doc_name in self.storage.get_collection_items(domain_name):
            content = self.storage.get_item(domain_name, doc_name)
            document = self.document_factory.create_document(name=doc_name, collection=domain_name, title=doc_name, content=content)
            documents.append(document)
        return documents

    def _get_collection_description(self, collection_name):
        # Implement this method
        pass
    
    def _get_domain_description(self, domain_name: str) -> str:  # Renamed method
        # This method should be implemented to fetch the description of a domain
        # For now, we'll return a placeholder
        return f"Description for {domain_name}"

    def get_domains(self) -> List[DomainInterface]:
        return list(self.domains.values())

    def get_domain(self, domain_name: str) -> DomainInterface:
        if domain_name not in self.domains:
            raise ValueError(f"Domain '{domain_name}' not found")
        return self.domains[domain_name]

    def apply_chunking_strategy(self) -> None:
        for domain in self.domains.values():
            for document in domain.documents:
                chunks = self.chunk_strategy.chunk_text(document.content)
                document.set_chunks(chunks)

    def get_domain_documents(self, domain_name: str) -> List[DocumentInterface]:
        domain = self.get_domain(domain_name)
        return domain.documents

    def get_domain_document(self, domain_name: str, document_name: str) -> DocumentInterface:
        documents = self.get_domain_documents(domain_name)
        for document in documents:
            if document.name == document_name:
                return document
        raise ValueError(f"Document '{document_name}' not found in domain '{domain_name}'")
