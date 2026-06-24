"""Analyst agent implementation."""

import logging

from multi_agent_research_lab.agents.base import BaseAgent
from multi_agent_research_lab.core.schemas import AgentName, AgentResult
from multi_agent_research_lab.core.state import ResearchState
from multi_agent_research_lab.observability.tracing import trace_span

logger = logging.getLogger(__name__)


class AnalystAgent(BaseAgent):
    """Turns research notes into structured insights."""

    name = "analyst"

    def run(self, state: ResearchState) -> ResearchState:
        """Populate `state.analysis_notes`."""

        logger.info("Analyst started")
        note_lines = [source.snippet for source in state.sources] or [state.research_notes or ""]
        with trace_span("analyst.run", {"sources": len(state.sources)}) as span:
            state.analysis_notes = (
                "Analysis:\n"
                f"- Key claim: {state.request.query} benefits from a staged workflow.\n"
                f"- Evidence summary: {' '.join(note_lines[:2])}\n"
                "- Risk: some sources may be vendor-authored or high-level.\n"
                "- Recommendation: preserve citations and call out uncertainty."
            )
            state.agent_results.append(
                AgentResult(
                    agent=AgentName.ANALYST,
                    content=state.analysis_notes,
                    metadata={"used_source_count": len(state.sources)},
                )
            )
            span["analysis_ready"] = True
        state.add_trace_event("analyst.completed", {"span": span})
        return state
