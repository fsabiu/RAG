from typing import List, Union
import logging
import requests
import numpy as np
from ...interfaces.embedding_model_interface import EmbeddingModelInterface

logger = logging.getLogger(__name__)

# https://github.com/ollama/ollama/blob/main/docs/faq.md
# Add Environment=OLLAMA_HOST=0.0.0.0:11434 to /etc/systemd/system/ollama.service 
class OllamaEmbedding(EmbeddingModelInterface):
    def __init__(self, model_name: str, ollama_host: str = "localhost", ollama_port: int = 11434):
        self._model_name = model_name
        self.base_url = f"http://{ollama_host}:{ollama_port}"
        
        logger.info(f"Initializing Ollama embedding model: {model_name}")
        logger.info(f"Ollama API URL: {self.base_url}")

    @property
    def model_name(self) -> str:
        return self._model_name

    def generate_embedding(self, chunks: Union[str, List[str]]) -> Union[List[float], List[List[float]]]:
        if isinstance(chunks, str):
            chunks = [chunks]
        
        logger.debug(f"Generating embeddings for {len(chunks)} chunk(s)")
        
        all_embeddings = []
        
        for chunk in chunks:
            try:
                response = requests.post(
                    f"{self.base_url}/api/embeddings",
                    json={
                        "model": self.model_name,
                        "prompt": chunk
                    }
                )
                response.raise_for_status()
                embedding = response.json()["embedding"]
                all_embeddings.append(embedding)
            except requests.RequestException as e:
                logger.error(f"Error generating embedding: {str(e)}")
                raise
            except KeyError as e:
                logger.error(f"Unexpected response structure: {str(e)}")
                raise
        
        return all_embeddings[0] if len(all_embeddings) == 1 else all_embeddings

