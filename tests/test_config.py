from pydantic_settings import SettingsConfigDict

from multi_agent_research_lab.core.config import Settings


def test_settings_defaults(monkeypatch) -> None:
    original_config = Settings.model_config
    Settings.model_config = SettingsConfigDict(
        env_file=None,
        env_file_encoding="utf-8",
        extra="ignore",
        populate_by_name=True,
    )
    try:
        for key in ("OPENAI_API_KEY", "OPENROUTER_API_KEY", "OPENROUTER_MODEL", "TAVILY_API_KEY"):
            monkeypatch.delenv(key, raising=False)
        settings = Settings()
        assert settings.openai_model
        assert settings.max_iterations >= 1
        assert settings.openrouter_api_key in (None, "")
        assert settings.openrouter_model in (None, "")
    finally:
        Settings.model_config = original_config
