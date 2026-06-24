"""Benchmark helpers for single-agent vs multi-agent."""

from time import perf_counter
from typing import Callable

from multi_agent_research_lab.core.schemas import BenchmarkMetrics
from multi_agent_research_lab.core.state import ResearchState


Runner = Callable[[str], ResearchState]


def run_benchmark(run_name: str, query: str, runner: Runner) -> tuple[ResearchState, BenchmarkMetrics]:
    """Measure latency and return practical benchmark metrics."""

    started = perf_counter()
    state = runner(query)
    latency = perf_counter() - started
    total_cost = 0.0
    cost_seen = False
    for item in state.agent_results:
        cost = item.metadata.get("cost_usd")
        if isinstance(cost, (int, float)):
            total_cost += float(cost)
            cost_seen = True
    citation_count = len([source for source in state.sources if source.url or source.title])
    coverage = 0.0 if not state.sources else min(1.0, citation_count / max(1, len(state.sources)))
    quality_score = 8.0 if state.final_answer and not state.errors else 5.0 if state.final_answer else 2.0
    notes = "Completed successfully." if not state.errors else "; ".join(state.errors)
    metrics = BenchmarkMetrics(
        run_name=run_name,
        latency_seconds=latency,
        estimated_cost_usd=total_cost if cost_seen else 0.0,
        quality_score=quality_score,
        citation_coverage=coverage,
        failure_rate=1.0 if state.errors else 0.0,
        notes=notes,
    )
    return state, metrics
