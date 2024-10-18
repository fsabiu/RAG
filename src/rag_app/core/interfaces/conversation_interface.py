from typing import List, Protocol
from pydantic import BaseModel

class Message(BaseModel):
    role: str
    content: str

class ConversationInterface(Protocol):
    def add_message(self, role: str, content: str) -> None:
        ...

    def get_history(self) -> List[Message]:
        ...

    def get_formatted_history(self) -> str:
        ...

    def clear(self) -> None:
        ...

    def get_last_n_messages_by_role(self, role: str, n: int) -> str:
        ...

