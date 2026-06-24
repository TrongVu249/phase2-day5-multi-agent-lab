"""Researcher agent implementation."""

import logging

from multi_agent_research_lab.agents.base import BaseAgent
from multi_agent_research_lab.core.schemas import AgentName, AgentResult
from multi_agent_research_lab.core.state import ResearchState
from multi_agent_research_lab.observability.tracing import trace_span
from multi_agent_research_lab.services.search_client import SearchClient

logger = logging.getLogger(__name__)


class ResearcherAgent(BaseAgent):
    """Collects sources and creates concise research notes."""

    name = "researcher"

    def __init__(self, search_client: SearchClient | None = None) -> None:
        self.search_client = search_client or SearchClient()

    def run(self, state: ResearchState) -> ResearchState:
        """Populate `state.sources` and `state.research_notes`."""

        logger.info("Researcher started for query: %s", state.request.query)
        with trace_span("researcher.run", {"query": state.request.query}) as span:
            sources = self.search_client.search(
                state.request.query,
                max_results=state.request.max_sources,
            )
            state.sources = sources[: state.request.max_sources]
            bullet_lines = [f"- {source.title}: {source.snippet}" for source in state.sources]
            state.research_notes = "Research notes:\n" + "\n".join(bullet_lines)
            state.agent_results.append(
                AgentResult(
                    agent=AgentName.RESEARCHER,
                    content=state.research_notes,
                    metadata={"source_count": len(state.sources)},
                )
            )
            span["source_count"] = len(state.sources)
        state.add_trace_event("researcher.completed", {"source_count": len(state.sources), "span": span})
        return state
