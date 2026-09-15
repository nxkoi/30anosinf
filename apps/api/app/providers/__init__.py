from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class ImageAnalysisProvider(ABC):
    """Interface for multimodal image analysis. Swap via IMAGE_PROVIDER env."""

    @abstractmethod
    def analyze(self, image: bytes, context: dict[str, Any]) -> dict[str, Any]:
        raise NotImplementedError


class LLMProvider(ABC):
    """Interface for text generation. Swap via LLM_PROVIDER env."""

    @abstractmethod
    def generate(self, messages: list[dict[str, str]], context: dict[str, Any]) -> dict[str, Any]:
        raise NotImplementedError


class MockImageAnalysisProvider(ImageAnalysisProvider):
    def analyze(self, image: bytes, context: dict[str, Any]) -> dict[str, Any]:
        return {
            "provider": "mock",
            "model": "mock-image-v0",
            "description": (
                "Descrição automática ainda não disponível. "
                "A imagem foi recebida e preparada para integração futura com a API multimodal."
            ),
            "structured_result": {
                "inference": True,
                "confidence": 0.0,
                "bytes_seen": len(image),
                "context_keys": sorted(context.keys()),
                "notes": "Mock provider — no external API was called.",
            },
            "status": "DONE",
        }


class MockLLMProvider(LLMProvider):
    def generate(self, messages: list[dict[str, str]], context: dict[str, Any]) -> dict[str, Any]:
        return {
            "provider": "mock",
            "model": "mock-llm-v0",
            "text": "Resposta simulada. Nenhuma API LLM real foi chamada.",
            "structured_result": {"messages": len(messages), "context": context},
        }


def get_image_provider() -> ImageAnalysisProvider:
    from app.config import get_settings

    name = get_settings().image_provider.lower()
    if name == "mock":
        return MockImageAnalysisProvider()
    # Future: openai, google, etc.
    return MockImageAnalysisProvider()


def get_llm_provider() -> LLMProvider:
    from app.config import get_settings

    name = get_settings().llm_provider.lower()
    if name == "mock":
        return MockLLMProvider()
    return MockLLMProvider()
