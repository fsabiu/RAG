from abc import ABC, abstractmethod
from typing import Dict, List
from .domain_interface import DomainInterface, DomainFactoryInterface
from .document_interface import DocumentInterface, DocumentFactoryInterface
from .storage_interface import StorageInterface
from .chunk_strategy_interface import ChunkStrategyInterface
from .chat_model_interface import ChatModelInterface
from .vector_store_interface import VectorStoreInterface, VectorStoreFactoryInterface
from .embedding_model_interface import EmbeddingModelInterface

class DomainManagerInterface(ABC):
    @abstractmethod
    def __init__(self, storage: StorageInterface, 
                 chunk_strategy: ChunkStrategyInterface, 
                 chat_model: ChatModelInterface, 
                 domain_factory: DomainFactoryInterface, 
                 document_factory: DocumentFactoryInterface,
                 vector_stores: Dict[str, VectorStoreInterface],
                 embedding_model: EmbeddingModelInterface,
                 vector_store_factory: VectorStoreFactoryInterface):
        pass

    @abstractmethod
    def get_domains(self) -> List[DomainInterface]:
        pass

    @abstractmethod
    def get_domain(self, domain_name: str) -> DomainInterface:
        pass

    @abstractmethod
    def apply_chunking_strategy(self) -> None:
        pass

    @abstractmethod
    def _create_domains(self) -> Dict[str, DomainInterface]:
        pass

    @abstractmethod
    def _create_documents(self, collection_name: str) -> List[DocumentInterface]:
        pass

    @abstractmethod
    def _get_collection_description(self, collection_name: str) -> str:
        pass
