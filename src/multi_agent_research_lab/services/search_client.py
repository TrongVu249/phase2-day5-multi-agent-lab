"""Search client abstraction for ResearcherAgent."""

import json
from urllib import request

from tenacity import retry, stop_after_attempt, wait_fixed

from multi_agent_research_lab.core.config import Settings, get_settings
from multi_agent_research_lab.core.schemas import SourceDocument


class SearchClient:
    """Provider-agnostic search client with fallback mock data."""

    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()

    def search(self, query: str, max_results: int = 5) -> list[SourceDocument]:
        """Search for documents relevant to a query."""

        if self.settings.tavily_api_key:
            try:
                return self._search_tavily(query, max_results=max_results)
            except Exception:
                pass
        return self._search_mock(query, max_results=max_results)

    @retry(stop=stop_after_attempt(2), wait=wait_fixed(1), reraise=True)
    def _search_tavily(self, query: str, max_results: int) -> list[SourceDocument]:
        payload = json.dumps(
            {
                "api_key": self.settings.tavily_api_key,
                "query": query,
                "max_results": max_results,
                "search_depth": "advanced",
            }
        ).encode("utf-8")
        http_request = request.Request(
            "https://api.tavily.com/search",
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with request.urlopen(http_request, timeout=self.settings.timeout_seconds) as response:  # noqa: S310
            raw = json.loads(response.read().decode("utf-8"))
        return [
            SourceDocument(
                title=item.get("title", "Untitled source"),
                url=item.get("url"),
                snippet=item.get("content", ""),
                metadata={"score": item.get("score")},
            )
            for item in raw.get("results", [])[:max_results]
        ]

    def _search_mock(self, query: str, max_results: int) -> list[SourceDocument]:
        lowered = query.lower()
        library = [
            SourceDocument(
                title="Anthropic - Building effective agents",
                url="https://www.anthropic.com/engineering/building-effective-agents",
                snippet=(
                    "Describes when agentic systems are useful, the value of decomposition,"
                    " and the cost of overly complex orchestration."
                ),
                metadata={"source_type": "reference"},
            ),
            SourceDocument(
                title="OpenAI - Agents orchestration and handoffs",
                url="https://developers.openai.com/api/docs/guides/agents/orchestration",
                snippet=(
                    "Covers supervisor-style orchestration, handoffs between roles, and tradeoffs"
                    " between autonomy and control."
                ),
                metadata={"source_type": "reference"},
            ),
            SourceDocument(
                title="LangGraph concepts",
                url="https://langchain-ai.github.io/langgraph/concepts/",
                snippet=(
                    "Explains graph-based workflow orchestration, state transitions, and"
                    " stop conditions for multi-step agent systems."
                ),
                metadata={"source_type": "reference"},
            ),
            SourceDocument(
                title="Guardrails for LLM applications",
                url="https://docs.smith.langchain.com/",
                snippet=(
                    "Summarizes tracing, observability, and debugging patterns that make"
                    " multi-agent systems easier to inspect."
                ),
                metadata={"source_type": "reference"},
            ),
        ]
        if "customer support" in lowered:
            library.append(
                SourceDocument(
                    title="Multi-agent workflows for customer support",
                    url=None,
                    snippet=(
                        "Customer support benefits from routing, knowledge retrieval, and"
                        " final response drafting, but latency and coordination overhead must be managed."
                    ),
                    metadata={"source_type": "mock"},
                )
            )
        if "graphrag" in lowered:
            library.append(
                SourceDocument(
                    title="GraphRAG state-of-the-art overview",
                    url=None,
                    snippet=(
                        "GraphRAG systems combine graph structure with retrieval to improve"
                        " multi-hop reasoning and evidence aggregation."
                    ),
                    metadata={"source_type": "mock"},
                )
            )
        return library[:max_results]
