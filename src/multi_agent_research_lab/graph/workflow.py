"""Workflow orchestration for the lab."""

import logging

from multi_agent_research_lab.agents import AnalystAgent, ResearcherAgent, SupervisorAgent, WriterAgent
from multi_agent_research_lab.agents.base import BaseAgent
from multi_agent_research_lab.core.config import Settings, get_settings
from multi_agent_research_lab.core.errors import AgentExecutionError, ValidationError
from multi_agent_research_lab.core.state import ResearchState
from multi_agent_research_lab.observability.tracing import trace_span

logger = logging.getLogger(__name__)


class MultiAgentWorkflow:
    """Builds and runs the multi-agent workflow."""

    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()

    def build(self) -> dict[str, BaseAgent]:
        """Create a workflow registry used by the internal orchestration loop."""

        return {
            "supervisor": SupervisorAgent(self.settings),
            "researcher": ResearcherAgent(),
            "analyst": AnalystAgent(),
            "writer": WriterAgent(),
        }

    def run(self, state: ResearchState) -> ResearchState:
        """Execute the workflow and return final state."""

        if not state.request.query.strip():
            raise ValidationError("Research query cannot be empty.")

        graph = self.build()
        supervisor = graph["supervisor"]

        while True:
            with trace_span("workflow.supervisor", {"iteration": state.iteration}) as span:
                state = supervisor.run(state)
                next_route = state.route_history[-1]
                span["route"] = next_route

            if next_route == "done":
                break

            agent = graph.get(next_route)
            if agent is None:
                raise AgentExecutionError(f"Unknown route selected by supervisor: {next_route}")

            try:
                state = agent.run(state)
            except Exception as exc:
                logger.exception("Agent %s failed", next_route)
                state.errors.append(f"{next_route} failed: {exc}")
                if state.iteration >= self.settings.max_iterations:
                    break
                state.final_answer = state.final_answer or (
                    "The workflow stopped early because one of the agents failed. "
                    "Review the trace and errors for details."
                )
                break

            if state.iteration >= self.settings.max_iterations and not state.final_answer:
                state.errors.append("Workflow stopped after reaching max iterations.")
                break

        if not state.final_answer:
            state.final_answer = (
                "The workflow completed without a final answer. Check research notes, analysis, and trace."
            )
        return state
