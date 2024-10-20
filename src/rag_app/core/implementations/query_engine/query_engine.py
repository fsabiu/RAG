import logging
from typing import List, Dict, Any, AsyncGenerator, Optional, Iterator, Union, AsyncIterator
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

    async def ask_question(
        self, 
        question: str, 
        domain_names: Optional[List[str]] = None, 
        model_name: str = "OCI_CommandRplus",
        conversation: ConversationInterface = None, 
        stream: bool = True
    ) -> Union[str, AsyncIterator[str]]:
        """
        Ask a question across multiple domains and stream the response in chunks.

        :param question: The user's question.
        :param domain_names: List of domain names to query. If None, query all available domains.
        :param conversation: The conversation interface.
        :param stream: Whether to stream the response.
        :return: The answer as a string or an asynchronous iterator of string chunks.
        """
        logger.info(f"Processing streamed question: '{question}'")

        # If domain_names is None, use all available vector store keys
        if domain_names is None:
            domain_names = list(self.domain_manager.vector_stores.keys())
            logger.debug(f"No specific domains provided. Using all domains: {domain_names}")
        else:
            # Validate that provided domains exist
            invalid_domains = [d for d in domain_names if d not in self.domain_manager.vector_stores]
            if invalid_domains:
                error_msg = f"Invalid domains specified: {invalid_domains}"
                logger.error(error_msg)
                raise ValueError(error_msg)
            logger.debug(f"Using specified domains: {domain_names}")

        combined_results = []

        for domain_name in domain_names:
            logger.info(f"Querying domain: {domain_name}")
            vector_store = self.domain_manager.vector_stores[domain_name]

            # Optimize the query and generate embeddings
            # optimized_query = self.query_optimizer.optimize(question)
            
            query_embedding = self.embedding_model.generate_embedding(question)

            # Query the vector store
            results = vector_store.query(query_embedding=query_embedding, n_results=self.n_results)
            logger.debug(f"Retrieved {len(results)} results from domain '{domain_name}'")

            # Append results with domain context
            for result in results:
                result['domain'] = domain_name
            combined_results.extend(results)

        # Re-rank all combined results if result_re_ranker is available
        if self.result_re_ranker is not None:
            ranked_results = self.result_re_ranker.re_rank(combined_results, question)
        else:
            ranked_results = combined_results

        logger.debug(f"Total combined results: {len(combined_results)}. Ranked results: {len(ranked_results)}")

        # Build context from top-ranked results
        context = "\n".join([result["document"] for result in ranked_results[:3]])
        prompt = f"Context: {context}\n\nQuestion: {question}\n\nAnswer:"

        logger.info("Generating response from chat model.")
        response = await self.chat_model.chat(system_prompt=prompt, query=question, stream=stream)

        if stream:
            return self._stream_response(response)
        else:
            return response.content if hasattr(response, 'content') else str(response)

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