from multi_agent_research_lab.agents import AnalystAgent, CriticAgent, ResearcherAgent, SupervisorAgent, WriterAgent
from multi_agent_research_lab.core.config import Settings
from multi_agent_research_lab.core.schemas import AgentName, ResearchQuery, SourceDocument
from multi_agent_research_lab.core.state import ResearchState
from multi_agent_research_lab.graph.workflow import MultiAgentWorkflow
from multi_agent_research_lab.services.llm_client import LLMClient, LLMResponse
from multi_agent_research_lab.services.search_client import SearchClient


class StubSearchClient(SearchClient):
    def __init__(self) -> None:
        pass

    def search(self, query: str, max_results: int = 5) -> list[SourceDocument]:
        return [
            SourceDocument(
                title="Test source",
                url="https://example.com",
                snippet=f"Evidence for {query}",
            )
        ][:max_results]


class StubLLMClient(LLMClient):
    def __init__(self, content: str) -> None:
        self.content = content

    def complete(self, system_prompt: str, user_prompt: str) -> LLMResponse:
        return LLMResponse(content=self.content, input_tokens=10, output_tokens=20, cost_usd=0.01)


def test_supervisor_routes_researcher_first() -> None:
    state = ResearchState(request=ResearchQuery(query="Explain multi-agent systems"))
    state = SupervisorAgent(Settings(max_iterations=6)).run(state)
    assert state.route_history == ["researcher"]


def test_supervisor_routes_done_after_critic_review() -> None:
    state = ResearchState(
        request=ResearchQuery(query="Explain multi-agent systems"),
        research_notes="notes",
        analysis_notes="analysis",
        final_answer="done",
        critic_notes="reviewed",
        review_status="passed",
    )
    state = SupervisorAgent(Settings(max_iterations=6)).run(state)
    assert state.route_history[-1] == "done"


def test_researcher_populates_sources_and_notes() -> None:
    state = ResearchState(request=ResearchQuery(query="Explain multi-agent systems"))
    result = ResearcherAgent(search_client=StubSearchClient()).run(state)
    assert result.sources
    assert result.research_notes is not None
    assert result.agent_results[0].agent == "researcher"


def test_analyst_populates_analysis_notes() -> None:
    state = ResearchState(
        request=ResearchQuery(query="Explain multi-agent systems"),
        research_notes="Research notes",
        sources=[SourceDocument(title="Test", url=None, snippet="Evidence snippet")],
    )
    result = AnalystAgent(
        llm_client=StubLLMClient(
            "Key claim: Test\nEvidence summary: Test\nRisk / uncertainty: Low\nRecommendation: Proceed"
        )
    ).run(state)
    assert result.analysis_notes is not None
    assert "Key claim" in result.analysis_notes


def test_writer_populates_final_answer() -> None:
    state = ResearchState(
        request=ResearchQuery(query="Explain multi-agent systems"),
        research_notes="Research notes",
        analysis_notes="Analysis",
        sources=[SourceDocument(title="Test", url=None, snippet="Evidence snippet")],
    )
    result = WriterAgent(llm_client=StubLLMClient("Answer body.\n\nReferences: Test")).run(state)
    assert result.final_answer is not None
    assert "References:" in result.final_answer


def test_critic_passes_when_references_present() -> None:
    state = ResearchState(
        request=ResearchQuery(query="Explain multi-agent systems"),
        final_answer="Answer body.\n\nReferences: Test",
    )
    result = CriticAgent().run(state)
    assert result.review_status == "passed"
    assert result.agent_results[-1].agent == AgentName.CRITIC


def test_critic_flags_missing_references() -> None:
    state = ResearchState(
        request=ResearchQuery(query="Explain multi-agent systems"),
        final_answer="Answer body only",
    )
    result = CriticAgent().run(state)
    assert result.review_status == "failed"
    assert result.errors


def test_workflow_runs_to_completion() -> None:
    state = ResearchState(request=ResearchQuery(query="Explain multi-agent systems"))
    workflow = MultiAgentWorkflow(settings=Settings(max_iterations=6))
    result = workflow.run(state)
    assert result.final_answer is not None
    assert result.route_history == ["researcher", "analyst", "writer", "critic", "done"]
    assert result.review_status == "passed"


def test_workflow_stops_at_max_iterations() -> None:
    state = ResearchState(request=ResearchQuery(query="Explain multi-agent systems"))
    workflow = MultiAgentWorkflow(settings=Settings(max_iterations=1))
    result = workflow.run(state)
    assert result.errors
