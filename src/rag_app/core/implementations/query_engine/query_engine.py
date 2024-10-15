import logging
from typing import List, Dict, Any
from ...interfaces.query_engine_interface import QueryEngineInterface
from ...interfaces.domain_manager_interface import DomainManagerInterface
from ...interfaces.vector_store_interface import VectorStoreInterface
from ...interfaces.query_optimizer_interface import QueryOptimizerInterface
from ...interfaces.reranker_interface import ReRankerInterface
from ...interfaces.embedding_model_interface import EmbeddingModelInterface
from ...interfaces.chat_model_interface import ChatModelInterface
from ...interfaces.chunk_strategy_interface import ChunkStrategyInterface

logger = logging.getLogger(__name__)

class QueryEngine(QueryEngineInterface):
    def __init__(self, 
                 domain_manager: DomainManagerInterface, 
                 vector_stores: Dict[str, VectorStoreInterface], 
                 embedding_model: EmbeddingModelInterface,
                 chat_model: ChatModelInterface,
                 chunk_strategy: ChunkStrategyInterface,
                 query_optimizer: QueryOptimizerInterface,
                 result_re_ranker: ReRankerInterface):
        self.domain_manager = domain_manager
        self.vector_stores = vector_stores
        self.embedding_model = embedding_model
        self.chat_model = chat_model
        self.chunk_strategy = chunk_strategy
        self.query_optimizer = query_optimizer
        self.result_re_ranker = result_re_ranker
        logger.info("QueryEngine initialized")

    def prepare_domains(self) -> None:
        logger.info("Preparing domains for offline processing")
        for domain in self.domain_manager.get_domains():
            self._prepare_domain(domain)

    def _prepare_domain(self, domain):
        logger.info(f"Preparing domain: {domain.name}")
        domain.summarize_documents()
        domain.chunk_documents(self.chunk_strategy)
        domain.embed_chunks(self.embedding_model)
        self._store_embeddings(domain)

    def _store_embeddings(self, domain):
        vector_store = self.vector_stores.get(domain.name)
        if vector_store:
            domain.store_embeddings(vector_store)
        else:
            logger.error(f"No vector store found for domain: {domain.name}")

    def ask_question(self, question: str, domain_name: str) -> Dict[str, Any]:
        logger.info(f"Processing question: {question} for domain: {domain_name}")
        try:
            domain = self.domain_manager.get_domain(domain_name)
            vector_store = self.vector_stores.get(domain_name)
            if not vector_store:
                raise ValueError(f"No vector store found for domain: {domain_name}")
        except ValueError as e:
            logger.error(f"Error finding domain or vector store: {str(e)}")
            raise

        optimized_query = self.query_optimizer.optimize(question)
        query_embedding = self.embedding_model.generate_embedding(optimized_query)
        results = vector_store.query(query_embedding)
        ranked_results = self.result_re_ranker.re_rank(results, question)
        
        context = "\n".join([result["document"] for result in ranked_results[:3]])
        prompt = f"Context: {context}\n\nQuestion: {question}\n\nAnswer:"
        response = self.chat_model.generate_response(prompt)
        
        logger.info(f"Generated response for question: {question}")
        return {"answer": response, "sources": ranked_results}
