from multi_agent_research_lab.agents import SupervisorAgent
from multi_agent_research_lab.core.config import Settings
from multi_agent_research_lab.core.schemas import ResearchQuery
from multi_agent_research_lab.core.state import ResearchState


def test_supervisor_routes_critic_after_writer() -> None:
    state = ResearchState(request=ResearchQuery(query="Explain multi-agent systems"))
    state.research_notes = "notes"
    state.analysis_notes = "analysis"
    state.final_answer = "answer with references\n\nReferences: Test"
    result = SupervisorAgent(Settings(max_iterations=6)).run(state)
    assert result.route_history[-1] == "critic"
