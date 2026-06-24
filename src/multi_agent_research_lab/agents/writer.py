"""Writer agent implementation."""

import logging

from multi_agent_research_lab.agents.base import BaseAgent
from multi_agent_research_lab.core.schemas import AgentName, AgentResult
from multi_agent_research_lab.core.state import ResearchState
from multi_agent_research_lab.observability.tracing import trace_span

logger = logging.getLogger(__name__)


class WriterAgent(BaseAgent):
    """Produces final answer from research and analysis notes."""

    name = "writer"

    def run(self, state: ResearchState) -> ResearchState:
        """Populate `state.final_answer`."""

        logger.info("Writer started")
        citations = ", ".join(source.title for source in state.sources[:3]) or "local workflow evidence"
        with trace_span("writer.run", {"citations": citations}) as span:
            state.final_answer = (
                f"Answer for '{state.request.query}':\n"
                "A multi-agent research workflow works best when supervision, evidence gathering,"
                " analysis, and final writing are separated into explicit steps. This improves"
                " debuggability and lets the system stop once each stage is complete.\n\n"
                f"Supporting analysis:\n{state.analysis_notes or 'No analysis available.'}\n\n"
                f"References: {citations}"
            )
            state.agent_results.append(
                AgentResult(
                    agent=AgentName.WRITER,
                    content=state.final_answer,
                    metadata={"citation_count": min(len(state.sources), 3)},
                )
            )
            span["final_answer_ready"] = True
        state.add_trace_event("writer.completed", {"span": span})
        return state
