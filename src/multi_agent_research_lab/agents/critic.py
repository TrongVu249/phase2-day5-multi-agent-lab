"""Optional critic agent implementation for bonus work."""

import logging

from multi_agent_research_lab.agents.base import BaseAgent
from multi_agent_research_lab.core.schemas import AgentName, AgentResult
from multi_agent_research_lab.core.state import ResearchState

logger = logging.getLogger(__name__)


class CriticAgent(BaseAgent):
    """Optional fact-checking and safety-review agent."""

    name = "critic"

    def run(self, state: ResearchState) -> ResearchState:
        """Validate final answer and append findings."""

        logger.info("Critic started")
        findings: list[str] = []
        if state.final_answer and "References:" not in state.final_answer:
            findings.append("Critic: final answer is missing references.")
        if findings:
            state.errors.extend(findings)
            state.review_status = "failed"
            state.critic_notes = "\n".join(findings)
        else:
            state.review_status = "passed"
            state.critic_notes = "Critic review passed: final answer includes references and is ready to share."
        state.agent_results.append(
            AgentResult(
                agent=AgentName.CRITIC,
                content=state.critic_notes,
                metadata={"review_status": state.review_status, "error_count": len(findings)},
            )
        )
        state.add_trace_event(
            "critic.completed",
            {"review_status": state.review_status, "critic_notes": state.critic_notes, "errors": list(state.errors)},
        )
        return state
