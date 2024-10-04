import logging
from typing import Dict, List
from ...interfaces.domain_manager_interface import DomainManagerInterface
from ...interfaces.domain_interface import DomainInterface
from ..document.document import Document
from ..domain.domain import Domain

logger = logging.getLogger(__name__)

class DomainManager(DomainManagerInterface):
    def __init__(self, storage, chunk_strategy, chat_model):
        self.storage = storage
        self.chunk_strategy = chunk_strategy
        self.chat_model = chat_model
        self.domains: Dict[str, Domain] = self._create_domains()

    def _create_domains(self) -> Dict[str, Domain]:
        domains = {}
        collections = self.storage.get_all_collections()
        
        for collection_name in collections:
            documents = self._create_documents(collection_name)
            description = self._get_collection_description(collection_name)
            domains[collection_name] = Domain(collection_name, description, documents)
        
        return domains

    def _create_documents(self, collection_name: str) -> List[Document]:
        documents = []
        collection_items = self.storage.get_collection_items(collection_name)
        
        for doc_name, content in collection_items.items():
            # Preprocess content if needed
            document = Document(doc_name, collection_name, content)
            documents.append(document)
        
        return documents

    def _get_collection_description(self, collection_name: str) -> str:
        # This method should be implemented to fetch the description of a collection
        # For now, we'll return a placeholder
        return f"Description for {collection_name}"

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
