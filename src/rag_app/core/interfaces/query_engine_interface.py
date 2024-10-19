from abc import ABC, abstractmethod
from typing import Dict, Any
from ...core.interfaces.conversation_interface import ConversationInterface
from typing import Optional, Iterator, Union, AsyncIterator

class QueryEngineInterface(ABC):
    @abstractmethod
    async def ask_question(self, question: str, domain_name: str, conversation: ConversationInterface, stream: bool = True) -> Union[str, AsyncIterator[str]]:
        pass
