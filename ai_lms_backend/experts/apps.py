from django.apps import AppConfig

from experts.services.llm_provider import LLMProvider


class ExpertsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "experts"

    def ready(self):
        LLMProvider.init()
        from rag_service.singleton import vector_store_service
        vector_store_service.initialize()
        from rag_service.singleton import rag_service
        rag_service.initialize()