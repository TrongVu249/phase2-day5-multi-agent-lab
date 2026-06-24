# Design Template

## Problem

Xay dung mot research assistant nhan query dai, thu thap thong tin lien quan, phan tich bang chung, va viet cau tra loi cuoi cung co the debug duoc. He thong can co ca baseline single-agent va workflow multi-agent de so sanh chat luong, latency, cost, va failure mode.

## Why multi-agent?

Single-agent phu hop voi query don gian, nhung kho debug khi can tach rieng retrieval, analysis, va answer drafting. Multi-agent giup moi buoc co responsibility ro rang, de trace, de benchmark, va de them guardrails nhu max iterations, fallback, va validation.

## Agent roles

| Agent | Responsibility | Input | Output | Failure mode |
|---|---|---|---|---|
| Supervisor | Chon worker tiep theo hoac dung workflow | `ResearchState` hien tai | Route tiep theo trong `route_history` | Dung som khi cham `max_iterations`, ghi loi vao `errors` |
| Researcher | Tim source, loc source, va tong hop research notes | User query, `max_sources` | `sources`, `research_notes` | Search provider fail thi fallback mock sources |
| Analyst | Rut key claims, tong hop evidence, flag weakness | `research_notes`, `sources` | `analysis_notes` | Nguon yeu hoac high-level thi ghi risk trong notes |
| Writer | Viet cau tra loi cuoi va gan references | `analysis_notes`, `sources` | `final_answer` | Neu workflow chua du context thi van tra loi ngan va neu limitation |

## Shared state

- `request`: query goc va runtime options nhu `max_sources`.
- `iteration`: dem so lan supervisor route de enforce stop condition.
- `route_history`: lich su route de debug workflow.
- `sources`: danh sach source da lay duoc.
- `research_notes`: output trung gian cua Researcher.
- `analysis_notes`: output trung gian cua Analyst.
- `final_answer`: cau tra loi cuoi cua Writer.
- `agent_results`: gom output va metadata cua tung agent de benchmark.
- `trace`: local trace events cho peer review va observability.
- `errors`: cac loi va fallback signal trong qua trinh chay.

## Routing policy

Workflow tuyen tinh va de debug:

`supervisor -> researcher -> analyst -> writer -> supervisor(done)`

Rule cu the:

- Neu chua co `research_notes` thi route `researcher`.
- Neu da co research nhung chua co `analysis_notes` thi route `analyst`.
- Neu da co analysis nhung chua co `final_answer` thi route `writer`.
- Neu da co `final_answer` thi route `done`.
- Neu `iteration >= max_iterations` thi route `done` va ghi loi.

## Guardrails

- Max iterations: doc tu `MAX_ITERATIONS`, default `6`.
- Timeout: doc tu `TIMEOUT_SECONDS`, default `60`, ap cho LLM/search clients.
- Retry: dung `tenacity` cho OpenAI va Tavily calls.
- Fallback: local LLM response va mock search sources khi thieu package, key, hoac network.
- Validation: query khong duoc rong; workflow dung neu route khong hop le.

## Benchmark plan

- Queries:
  - `Research GraphRAG state-of-the-art and write a 500-word summary`
  - `Compare single-agent and multi-agent workflows for customer support`
  - `Summarize production guardrails for LLM agents`
- Metrics:
  - Latency: wall-clock time
  - Cost: tong `cost_usd` trong `agent_results`
  - Quality: rubric 0-10 hoac heuristic score
  - Citation coverage: ty le source duoc dua vao output
  - Failure rate: co loi hay khong tren moi run
- Expected outcome:
  - Baseline nhanh hon nhung it trace hon.
  - Multi-agent cham hon nhung de explain, de debug, va de bao toan citations hon.
