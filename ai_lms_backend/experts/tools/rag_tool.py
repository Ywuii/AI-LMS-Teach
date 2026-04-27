from typing import Dict, Any, List

class RAGTool:
    def __init__(self, rag_service):
        self.rag_service = rag_service

    def retrieve(
        self,
        question: str,
        domain: str = "general",
        use_kg: bool = True,
        use_rag: bool = True
    ) -> Dict[str, Any]:

        result = {
            "vector": [],
            "kg": []
        }

        if use_rag:
            result["vector"] = self.rag_service.retrieve_vector(question)

        if use_kg:
            result["kg"] = self.rag_service.retrieve_kg(
                question=question,
                domain=domain
            )

        return result