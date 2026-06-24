"""LLM client abstraction.

Production note: agents should depend on this interface instead of importing an SDK directly.
"""

from dataclasses import dataclass
from typing import Any

from tenacity import retry, stop_after_attempt, wait_fixed

from multi_agent_research_lab.core.config import Settings, get_settings


@dataclass(frozen=True)
class LLMResponse:
    content: str
    input_tokens: int | None = None
    output_tokens: int | None = None
    cost_usd: float | None = None


class LLMClient:
    """Provider-agnostic LLM client with graceful local fallback."""

    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()

    def complete(self, system_prompt: str, user_prompt: str) -> LLMResponse:
        """Return a model completion."""

        if self.settings.openai_api_key:
            try:
                return self._complete_openai(system_prompt, user_prompt)
            except Exception:
                pass
        return self._complete_locally(system_prompt, user_prompt)

    @retry(stop=stop_after_attempt(2), wait=wait_fixed(1), reraise=True)
    def _complete_openai(self, system_prompt: str, user_prompt: str) -> LLMResponse:
        try:
            from openai import OpenAI
        except ImportError as exc:  # pragma: no cover - optional dependency
            raise RuntimeError("openai package is not installed") from exc

        client = OpenAI(api_key=self.settings.openai_api_key, timeout=self.settings.timeout_seconds)
        response = client.responses.create(
            model=self.settings.openai_model,
            input=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        )
        content = self._extract_response_text(response)
        usage = getattr(response, "usage", None)
        input_tokens = getattr(usage, "input_tokens", None)
        output_tokens = getattr(usage, "output_tokens", None)
        return LLMResponse(
            content=content,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cost_usd=self._estimate_cost(input_tokens, output_tokens),
        )

    def _complete_locally(self, system_prompt: str, user_prompt: str) -> LLMResponse:
        content = self._render_fallback_content(system_prompt, user_prompt)
        input_tokens = self._estimate_tokens(system_prompt) + self._estimate_tokens(user_prompt)
        output_tokens = self._estimate_tokens(content)
        return LLMResponse(
            content=content,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cost_usd=0.0,
        )

    def _render_fallback_content(self, system_prompt: str, user_prompt: str) -> str:
        prompt = user_prompt.strip()
        lowered_system = system_prompt.lower()
        if "analysis" in lowered_system:
            return (
                "Analysis:\n"
                "- Primary claim: the topic benefits from decomposition into explicit steps.\n"
                "- Supporting evidence: multiple references emphasize process, quality, and guardrails.\n"
                "- Weakness: some evidence may come from vendor-authored sources.\n"
                "- Recommendation: keep citations and mention uncertainty."
            )
        if "writer" in lowered_system or "final answer" in lowered_system:
            return (
                f"Summary for '{prompt}':\n"
                "Use a structured workflow that gathers evidence, analyzes tradeoffs, and then writes a"
                " concise response. Include source references, note uncertainty, and stop once the core"
                " question has been answered."
            )
        if "research" in lowered_system:
            return (
                "Research notes:\n"
                f"- Topic: {prompt}\n"
                "- Focus on current practices, tradeoffs, and implementation constraints.\n"
                "- Capture source-backed claims before moving to analysis."
            )
        return (
            f"Response for '{prompt}':\n"
            "This baseline answer was generated locally because an external LLM provider was not"
            " available. It still follows the requested structure and highlights the main ideas."
        )

    def _extract_response_text(self, response: Any) -> str:
        output_text = getattr(response, "output_text", None)
        if isinstance(output_text, str) and output_text.strip():
            return output_text
        chunks: list[str] = []
        for item in getattr(response, "output", []):
            for content in getattr(item, "content", []):
                text = getattr(content, "text", None)
                if text:
                    chunks.append(text)
        if chunks:
            return "\n".join(chunks)
        raise RuntimeError("OpenAI response did not include text output")

    def _estimate_tokens(self, text: str) -> int:
        return max(1, len(text.split()) * 2)

    def _estimate_cost(self, input_tokens: int | None, output_tokens: int | None) -> float | None:
        if input_tokens is None or output_tokens is None:
            return None
        pricing = {
            "gpt-4o-mini": (0.15, 0.60),
            "gpt-4.1-mini": (0.40, 1.60),
        }
        input_rate, output_rate = pricing.get(self.settings.openai_model, (0.15, 0.60))
        return ((input_tokens / 1_000_000) * input_rate) + ((output_tokens / 1_000_000) * output_rate)
