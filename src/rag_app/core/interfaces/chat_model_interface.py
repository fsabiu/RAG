from abc import ABC, abstractmethod
from typing import Optional, Iterator, Union

class ChatModelInterface(ABC):
    @abstractmethod
    def chat(self, system_prompt: str, query: str, stream: bool = False) -> Union[str, Iterator[str]]:
        pass
