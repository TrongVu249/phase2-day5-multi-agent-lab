# Benchmark Report

This report is ready to be updated after running the baseline and multi-agent flows locally. The markdown renderer in `multi_agent_research_lab.evaluation.report` uses the same structure.

| Run | Latency (s) | Cost (USD) | Quality | Citation Coverage | Failure Rate | Notes |
|---|---:|---:|---:|---:|---:|---|
| baseline | TBD | TBD | TBD | TBD | TBD | Replace with actual benchmark results. |
| multi-agent | TBD | TBD | TBD | TBD | TBD | Replace with actual benchmark results. |

## Quality Notes

- Baseline is expected to be simpler and faster, but harder to inspect.
- Multi-agent is expected to produce clearer intermediate artifacts and better evidence handling.
- Add screenshots or trace links here after running the workflow in your environment.

## Failure Modes And Fixes

- Missing or weak sources:
  - Integrate Tavily or another search provider and add stronger filtering.
- High latency:
  - Reduce iterations, tighten prompts, or skip analysis for trivial queries.
- Incomplete answers:
  - Tighten supervisor routing and validate writer output before stopping.

## Exit Ticket Draft

1. Nen dung multi-agent khi task can tach retrieval, analysis, va writing de de debug va de control quality.
2. Khong nen dung multi-agent khi query ngan, thoi gian phan hoi quan trong hon, hoac coordination overhead lon hon gia tri mang lai.
