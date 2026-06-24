"""Optional critic agent implementation for bonus work."""

from multi_agent_research_lab.agents.base import BaseAgent
from multi_agent_research_lab.core.state import ResearchState


class CriticAgent(BaseAgent):
    """Optional fact-checking and safety-review agent."""

    name = "critic"

    def run(self, state: ResearchState) -> ResearchState:
        """Validate final answer and append findings."""

        if state.final_answer and "References:" not in state.final_answer:
            state.errors.append("Critic: final answer is missing references.")
        state.add_trace_event("critic.completed", {"errors": list(state.errors)})
        return state
