from abc import ABC, abstractmethod
from typing import Dict, Any


class BaseExpertAgent(ABC):

    def __init__(self, rag_service):
        self.rag_service = rag_service

    @abstractmethod
    def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        pass