from multi_agent_research_lab.core.config import Settings
from multi_agent_research_lab.services.llm_client import LLMClient


def test_llm_client_uses_openrouter_model_when_available() -> None:
    client = LLMClient(
        Settings(
            openrouter_api_key="test-key",
            openrouter_model="openai/gpt-4o-mini",
            openai_model="gpt-4o-mini",
        )
    )
    assert client._get_model_name() == "openai/gpt-4o-mini"


def test_llm_client_falls_back_to_openai_model_for_openrouter() -> None:
    client = LLMClient(
        Settings(
            openrouter_api_key="test-key",
            openrouter_model=None,
            openai_model="gpt-4o-mini",
        )
    )
    assert client._get_model_name() == "gpt-4o-mini"
