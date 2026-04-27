from typing import Optional

from langchain_ollama import OllamaLLM


# 或你自己的本地 LLM

class LLMProvider:
    _llm: Optional[OllamaLLM] = None

    @classmethod
    def init(cls):
        if cls._llm is None:
            cls._llm = OllamaLLM(
                model="clidx/Qwen3-1.7B-Q8_0:think",
                temperature=0.2,
                streaming=True
            )

    @classmethod
    def get_llm(cls):
        if cls._llm is None:
            raise RuntimeError("LLM 尚未初始化")
        return cls._llm