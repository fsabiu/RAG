from typing import List
from ...interfaces.domain_interface import DomainFactoryInterface, DomainInterface
from ...interfaces.document_interface import DocumentInterface
from .domain import Domain

class DomainFactory(DomainFactoryInterface):
    def create_domain(self, name: str, description: str, documents: List[DocumentInterface]) -> DomainInterface:
        return Domain(name, description, documents)
