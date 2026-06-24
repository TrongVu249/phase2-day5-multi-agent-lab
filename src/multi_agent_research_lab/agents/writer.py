"""Writer agent implementation."""

import logging

from multi_agent_research_lab.agents.base import BaseAgent
from multi_agent_research_lab.core.schemas import AgentName, AgentResult
from multi_agent_research_lab.core.state import ResearchState
from multi_agent_research_lab.observability.tracing import trace_span
from multi_agent_research_lab.services.llm_client import LLMClient

logger = logging.getLogger(__name__)


class WriterAgent(BaseAgent):
    """Produces final answer from research and analysis notes."""

    name = "writer"

    def __init__(self, llm_client: LLMClient | None = None) -> None:
        self.llm_client = llm_client or LLMClient()

    def run(self, state: ResearchState) -> ResearchState:
        """Populate `state.final_answer`."""

        logger.info("Writer started")
        citations = [source.title for source in state.sources[:3]]
        citation_text = ", ".join(citations) or "local workflow evidence"
        user_prompt = (
            f"Query: {state.request.query}\n"
            f"Audience: {state.request.audience}\n\n"
            f"Research notes:\n{state.research_notes or 'No research notes available.'}\n\n"
            f"Analysis notes:\n{state.analysis_notes or 'No analysis available.'}\n\n"
            "References to include:\n- "
            + "\n- ".join(citations or ["local workflow evidence"])
            + "\n\nWrite a concise final answer with a brief explanation, a short limitations note,"
            " and a final line that starts with 'References:'."
        )
        with trace_span("writer.run", {"citations": citation_text}) as span:
            response = self.llm_client.complete(
                system_prompt=(
                    "You are the Writer agent in a multi-agent research workflow. Write a concise,"
                    " helpful answer for technical learners. Preserve uncertainty where evidence is"
                    " weak, and always end with a 'References:' line."
                ),
                user_prompt=user_prompt,
            )
            state.final_answer = response.content
            if "References:" not in state.final_answer:
                state.final_answer = f"{state.final_answer.rstrip()}\n\nReferences: {citation_text}"
            state.agent_results.append(
                AgentResult(
                    agent=AgentName.WRITER,
                    content=state.final_answer,
                    metadata={
                        "citation_count": min(len(state.sources), 3),
                        "input_tokens": response.input_tokens,
                        "output_tokens": response.output_tokens,
                        "cost_usd": response.cost_usd,
                    },
                )
            )
            span["final_answer_ready"] = True
        state.add_trace_event("writer.completed", {"span": span})
        return state
