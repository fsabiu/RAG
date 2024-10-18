import logging
from abc import ABC, abstractmethod
from langchain_community.chat_models import ChatOCIGenAI
from langchain_core.prompts import PromptTemplate
from typing import Optional, Iterator, Union, AsyncIterator
import oci
from rag_app.core.interfaces.chat_model_interface import ChatModelInterface
from ...interfaces.conversation_interface import ConversationInterface
from rag_app.core.implementations.conversation.conversation import Conversation

# Enable debug logging for the entire oci package
#logging.getLogger('oci').setLevel(logging.DEBUG)

# Enable request logging
oci.base_client.is_http_log_enabled(True)

logger = logging.getLogger(__name__)

class ChatModel(ChatModelInterface):
    @abstractmethod
    def __init__(self):
        pass

    @property
    @abstractmethod
    def llm(self):
        pass

    async def chat(self, system_prompt: str, query: str, conversation: Optional[ConversationInterface] = Conversation(), stream: bool = False) -> Union[str, AsyncIterator[str]]:
        prompt_template = f"{system_prompt}\n\n"
        
        if conversation:
            prompt_template += f"{conversation.get_formatted_history()}\n\n"
        
        prompt_template += "User: {query}\n\nAssistant:"
        prompt = PromptTemplate(input_variables=["query"], template=prompt_template)
        
        # Log the final prompt
        logger.info(f"History: {conversation.get_formatted_history()}\n\n")
        logger.info(f"Final prompt: {prompt.format(query=query)}")
        
        llm_chain = prompt | self.llm

        if stream:
            return self._stream_response(llm_chain, query)
        else:
            return await self._generate_response(llm_chain, query)

    async def _generate_response(self, llm_chain, query: str) -> str:
        logger.info(f"Generating response with {self.__class__.__name__} for query: {query[:50]}...")
        response = await llm_chain.ainvoke(query)
        
        return response

    async def _stream_response(self, llm_chain, query: str) -> AsyncIterator[str]:
        logger.info(f"Streaming response with {self.__class__.__name__} for query: {query[:50]}...")
        full_response = ""
        
        async for chunk in llm_chain.astream(query):
            if chunk.content is not None:
                full_response += chunk.content
                yield chunk.content

class OCI_CommandRplus(ChatModel, ChatModelInterface):
    def __init__(self, settings: dict):
        logger.info("Initializing OCI_CommandRplus chat model")
        
        # Use the settings dictionary to fetch parameters
        llm_params = {
            "model_id": settings["MODEL_ID"],
            "service_endpoint": settings["OCI_GENAI_ENDPOINT"],
            "compartment_id": settings["OCI_COMPARTMENT_ID"],
            "auth_type": "API_KEY",
            "auth_profile": settings["OCI_CONFIG_PROFILE"],
            "model_kwargs": {
                "temperature": settings["TEMPERATURE"],
                "max_tokens": settings["MAX_TOKENS"],
                "top_p": settings["TOP_P"]
            }
        }
        
        self._llm = ChatOCIGenAI(**llm_params)

    @property
    def llm(self):
        return self._llm

class OCI_Llama3_70(ChatModel, ChatModelInterface):
    def __init__(self, settings: dict):
        logger.info("Initializing OCI_Llama3-70 chat model")
        llm_params = {
            "model_id": settings["MODEL_ID_LLAMA3"],
            "service_endpoint": settings["OCI_GENAI_ENDPOINT"],
            "compartment_id": settings["OCI_COMPARTMENT_ID"],
            "auth_type": "API_KEY",
            "auth_profile": settings["OCI_CONFIG_PROFILE"],
            "model_kwargs": {
                "temperature": settings["TEMPERATURE"],
                "max_tokens": settings["MAX_TOKENS"],
                "top_p": settings["TOP_P"]
            }
        }
        self._llm = ChatOCIGenAI(**llm_params)

    @property
    def llm(self):
        return self._llm
