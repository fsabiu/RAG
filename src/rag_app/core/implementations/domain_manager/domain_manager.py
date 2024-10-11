import logging
from typing import Dict, List
from concurrent.futures import ThreadPoolExecutor, as_completed
from ...interfaces.domain_manager_interface import DomainManagerInterface
from ...interfaces.domain_interface import DomainInterface
from ...interfaces.document_interface import DocumentInterface
from ...interfaces.storage_interface import StorageInterface
from ...interfaces.chunk_strategy_interface import ChunkStrategyInterface
from ...interfaces.chat_model_interface import ChatModelInterface
from ...interfaces.vector_store_interface import VectorStoreInterface
from ..document.document import Document
from ..domain.domain import Domain

logger = logging.getLogger(__name__)

class DomainManager(DomainManagerInterface):
    def __init__(self, storage, chunk_strategy, chat_model, domain_factory, document_factory, vector_store: VectorStoreInterface):
        self.storage = storage
        self.chunk_strategy = chunk_strategy
        self.chat_model = chat_model
        self.vector_store = vector_store
        self.domain_factory = domain_factory
        self.document_factory = document_factory
        self.domains: Dict[str, DomainInterface] = {}
        self._create_domains()

    def _create_domains(self) -> None:
        domain_names = self.storage.get_all_collections()
        
        with ThreadPoolExecutor() as executor:
            future_to_domain = {executor.submit(self._create_domain, domain_name): domain_name for domain_name in domain_names}
            for future in as_completed(future_to_domain):
                domain_name = future_to_domain[future]
                try:
                    domain = future.result()
                    self.domains[domain_name] = domain
                except Exception as exc:
                    logger.error(f"Error creating domain {domain_name}: {exc}")

    def _create_domain(self, domain_name: str) -> DomainInterface:
        documents = self._create_documents(domain_name)
        description = self._get_domain_description(domain_name)
        return self.domain_factory.create_domain(domain_name, description, documents)

    def _create_documents(self, domain_name: str) -> List[DocumentInterface]:
        documents = []
        for doc_name in self.storage.get_collection_items(domain_name):
            # Create document without content, implement lazy loading
            document = self.document_factory.create_document(name=doc_name, collection=domain_name, title=doc_name, content=None)
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
        strategy_name = self.chunk_strategy.strategy_name
        strategy_params = self.chunk_strategy.get_parameters()
        
        logger.info(f"Applying chunking strategy: {strategy_name}")
        logger.info(f"Strategy parameters: {strategy_params}")

        for domain in self.domains.values():
            logger.info(f"Applying chunking strategy to domain: {domain.name}")
            for document in domain.documents:
                if document.get_content() is None:
                    content = self.storage.get_item(domain.name, document.name)
                    document.set_content(content)
                content = document.get_content()
                if content is None:
                    logger.warning(f"Document {document.name} in domain {domain.name} has no content after attempted load")
                    continue
                chunks = self.chunk_strategy.chunk_text(content)
                document.set_chunks(chunks)
                logger.debug(f"Chunked document {document.name} in domain {domain.name} into {len(chunks)} chunks")
                
                # Store embeddings and clear chunks from memory
                self.store_embedded_documents(domain.name, document)
                document.set_chunks([])  # Clear chunks from memory
                document.set_content(None)  # Clear content from memory

    def store_embedded_documents(self, domain_name: str, document: DocumentInterface) -> None:
        logger.info(f"Storing embedded documents for {document.name} in domain {domain_name}")
        chunks = document.get_chunks()
        embeddings = []
        metadata = []
        ids = []
        documents = []
        
        for i, chunk in enumerate(chunks):
            embedding = self.chat_model.get_embedding(chunk)
            embeddings.append(embedding)
            metadata.append({
                "domain": domain_name,
                "document": document.name,
                "chunk_index": i
            })
            ids.append(f"{domain_name}_{document.name}_{i}")
            documents.append(chunk)
        
        # Store the embedded chunks in the vector store
        self.vector_store.store_embeddings(embeddings, metadata, ids, documents)
        logger.debug(f"Stored {len(embeddings)} embedded chunks for document {document.name} in domain {domain_name}")

    def get_domain_documents(self, domain_name: str) -> List[DocumentInterface]:
        domain = self.get_domain(domain_name)
        return domain.documents

    def get_domain_document(self, domain_name: str, document_name: str) -> DocumentInterface:
        documents = self.get_domain_documents(domain_name)
        for document in documents:
            if document.name == document_name:
                if document.get_content() is None:
                    # Lazy load content when needed
                    logger.debug(f"Lazy loading content for document {document_name} in domain {domain_name}")
                    content = self.storage.get_item(domain_name, document_name)
                    document.set_content(content)
                return document
        raise ValueError(f"Document '{document_name}' not found in domain '{domain_name}'")