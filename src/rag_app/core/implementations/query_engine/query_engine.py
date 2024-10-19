import logging
from typing import List, Dict, Any, AsyncGenerator
from ...interfaces.query_engine_interface import QueryEngineInterface
from ...interfaces.domain_manager_interface import DomainManagerInterface
from ...interfaces.vector_store_interface import VectorStoreInterface
from ...interfaces.query_optimizer_interface import QueryOptimizerInterface
from ...interfaces.reranker_interface import ReRankerInterface
from ...interfaces.embedding_model_interface import EmbeddingModelInterface
from ...interfaces.chat_model_interface import ChatModelInterface
from ...interfaces.chunk_strategy_interface import ChunkStrategyInterface
from ...interfaces.conversation_interface import ConversationInterface

import time
import json
from typing import Optional, Iterator, Union, AsyncIterator

logger = logging.getLogger(__name__)

class QueryEngine(QueryEngineInterface):
    def __init__(self, 
                 domain_manager: DomainManagerInterface, 
                 vector_stores: Dict[str, VectorStoreInterface], 
                 embedding_model: EmbeddingModelInterface,
                 chat_model: ChatModelInterface,
                 chunk_strategy: ChunkStrategyInterface,
                 query_optimizer: QueryOptimizerInterface,
                 result_re_ranker: ReRankerInterface,
                 n_results: int = 5):
        self.domain_manager = domain_manager
        self.vector_stores = vector_stores
        self.embedding_model = embedding_model
        self.chat_model = chat_model
        self.query_optimizer = query_optimizer
        self.result_re_ranker = result_re_ranker
        self.n_results = n_results
        logger.info("QueryEngine initialized")

    @property
    def n_results(self) -> int:
        return self._n_results

    @n_results.setter
    def n_results(self, value: int):
        if not isinstance(value, int) or value <= 0:
            raise ValueError("n_results must be a positive integer")
        self._n_results = value
        logger.info(f"n_results updated to {value}")

    async def send_initial_message(self, model_name: str, prompt: str, stream: bool = True) -> Union[str, AsyncIterator[str]]:
        """
        Send the initial prompt to the chat model and yield responses in chunks.
        """
        logger.info(f"Sending initial message with model: {model_name}")
        response = await self.chat_model.chat(prompt, "", stream=stream)
        
        if stream:
            return self._stream_response(response)
        else:
            return response.content if hasattr(response, 'content') else str(response)

    async def ask_question(self, question: str, domain_name: str, conversation: ConversationInterface, stream: bool = True) -> Union[str, AsyncIterator[str]]:
        """
        Ask a question and stream the response in chunks.
        """
        logger.info(f"Processing streamed question: {question} for domain: {domain_name}")
        try:
            domain = self.domain_manager.get_domain(domain_name)
            vector_store = self.vector_stores.get(domain_name)
            if not vector_store:
                raise ValueError(f"No vector store found for domain: {domain_name}")
        except ValueError as e:
            logger.error(f"Error finding domain or vector store: {str(e)}")
            raise

        # optimized_query = self.query_optimizer.optimize(question)
        # query_embedding = self.embedding_model.generate_embedding(optimized_query)
        results = vector_store.query(query_embedding=query_embedding, n_results=self.n_results)
        ranked_results = self.result_re_ranker.re_rank(results, question)
        
        context = "\n".join([result["document"] for result in ranked_results[:3]])
        prompt = f"Context: {context}\n\nQuestion: {question}\n\nAnswer:"
        
        async for chunk in self.chat_model.chat(system_prompt=prompt, query=question, stream=stream):
            yield chunk
    
    def initialize_chat_model(self, gen_model: str, init_prompt: str) -> Dict[str, Any]:
        """
        Initialize the chat model with the provided generation model and initial prompt.
        """
        logger.info(f"Initializing chat model with model: {gen_model}")
        try:
            # Here you might have specific initialization logic based on the model
            prompt = init_prompt
            response = self.chat_model.generate_response(prompt)
            logger.info("Chat model initialized successfully.")
            return {"message": response}
        except Exception as e:
            logger.error(f"Failed to initialize chat model: {str(e)}")
            raise

    async def _stream_response(self, response: AsyncIterator[str]) -> AsyncIterator[str]:
        async for chunk in response:
            yield chunk