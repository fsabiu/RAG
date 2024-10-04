import logging
from rag_app.config import settings
from langchain_community.chat_models import ChatOCIGenAI
from langchain_core.prompts import PromptTemplate
from typing import Optional, Iterator, Union
import oci
from rag_app.core.interfaces.chat_model import ChatModel

# Enable debug logging for the entire oci package
logging.getLogger('oci').setLevel(logging.DEBUG)

# Enable request logging
oci.base_client.is_http_log_enabled(True)

logger = logging.getLogger(__name__)

class OCI_CommandRplus(ChatModel):
    def __init__(self):
        logger.info("Initializing OCI_CommandRplus chat model")
        self.llm = ChatOCIGenAI(
            model_id=settings.chat_model.MODEL_ID,
            service_endpoint=settings.chat_model.OCI_GENAI_ENDPOINT,
            compartment_id=settings.chat_model.OCI_COMPARTMENT_ID,
            auth_type="API_KEY",
            auth_profile=settings.chat_model.OCI_CONFIG_PROFILE,
            model_kwargs={
                "temperature": settings.chat_model.TEMPERATURE,
                "max_tokens": settings.chat_model.MAX_TOKENS,
                "top_p": settings.chat_model.TOP_P
            }
        )

    def chat(self, system_prompt: str, query: str, stream: bool = False) -> Union[str, Iterator[str]]:
        prompt_template = f"{system_prompt}\n\nHuman: {{query}}\n\nAssistant:"
        prompt = PromptTemplate(input_variables=["query"], template=prompt_template)
        llm_chain = prompt | self.llm

        if stream:
            return self._stream_response(llm_chain, query)
        else:
            return self._generate_response(llm_chain, query)

    def _generate_response(self, llm_chain, query: str) -> str:
        logger.info(f"Generating response with OCI_CommandRplus for query: {query[:50]}...")
        response = llm_chain.invoke(query)
        return response

    def _stream_response(self, llm_chain, query: str) -> Iterator[str]:
        logger.info(f"Streaming response with OCI_CommandRplus for query: {query[:50]}...")
        for chunk in llm_chain.stream(query):
            yield chunk

class OCI_Llama3_70(ChatModel):
    def __init__(self):
        logger.info("Initializing OCI_Llama3-70 chat model")
        # Add any specific initialization for OCI_Llama3-70
        self.api_key = settings.OCI_API_KEY

    def chat(self, system_prompt: str, query: str, stream: bool = False) -> Union[str, Iterator[str]]:
        logger.info(f"Generating response with OCI_Llama3-70 for prompt: {query[:50]}...")
        # Implement the logic to generate a response using OCI_Llama3-70
        pass
