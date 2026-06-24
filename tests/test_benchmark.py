from multi_agent_research_lab.core.schemas import AgentName, AgentResult, ResearchQuery, SourceDocument
from multi_agent_research_lab.core.state import ResearchState
from multi_agent_research_lab.evaluation.benchmark import run_benchmark


def test_benchmark_returns_metrics() -> None:
    def runner(query: str) -> ResearchState:
        state = ResearchState(request=ResearchQuery(query=query))
        state.sources = [SourceDocument(title="Source", url="https://example.com", snippet="Snippet")]
        state.final_answer = "Answer"
        state.agent_results.append(
            AgentResult(
                agent=AgentName.WRITER,
                content="Answer",
                metadata={"cost_usd": 0.12},
            )
        )
        return state

    _, metrics = run_benchmark("baseline", "Explain multi-agent systems", runner)
    assert metrics.run_name == "baseline"
    assert metrics.latency_seconds >= 0
    assert metrics.estimated_cost_usd == 0.12
    assert metrics.citation_coverage == 1.0
