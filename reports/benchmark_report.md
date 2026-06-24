# Báo Cáo Benchmark

Báo cáo này tổng hợp 3 truy vấn benchmark được chạy local vào ngày June 24, 2026 với phiên bản baseline và multi-agent hiện tại. Baseline dùng một lần gọi `LLMClient`. Multi-agent chạy theo luồng `Supervisor -> Researcher -> Analyst -> Writer -> Critic -> Done`.

| Lượt chạy | Độ trễ (s) | Chi phí (USD) | Chất lượng | Độ bao phủ trích dẫn | Tỷ lệ lỗi | Ghi chú |
|---|---:|---:|---:|---:|---:|---|
| trung bình baseline (3 truy vấn) | 9.26 | 0.0002 | 8.0 | 0% | 0% | Nhanh nhất, nhưng không có danh sách nguồn hay artifact trace nội bộ. |
| trung bình multi-agent (3 truy vấn) | 21.85 | 0.0013 | 8.0 | 100% | 0% | Chậm hơn và tốn chi phí hơn, nhưng ổn định trong việc tạo source, route history và critic review. |

## Kết Quả Từng Truy Vấn

| Truy vấn | Lượt chạy | Độ trễ (s) | Chi phí (USD) | Chất lượng | Độ bao phủ trích dẫn | Tỷ lệ lỗi | Ghi chú |
|---|---|---:|---:|---:|---:|---:|---|
| GraphRAG state-of-the-art | baseline | 18.83 | 0.0004 | 8.0 | 0% | Bài tóm tắt dài và ổn, nhưng không có trích dẫn hay artifact trung gian. |
| GraphRAG state-of-the-art | multi-agent | 25.95 | 0.0014 | 8.0 | 100% | Xử lý bằng chứng tốt nhất trong 3 truy vấn; critic pass và references được giữ lại. |
| Customer support workflows | baseline | 3.60 | 0.0001 | 8.0 | 0% | Nhanh và dễ đọc, nhưng phần tradeoff còn nông. |
| Customer support workflows | multi-agent | 15.11 | 0.0011 | 8.0 | 100% | Thể hiện chuyên môn hóa và tradeoff rõ hơn, nhưng đổi lại độ trễ tăng nhiều. |
| Production guardrails | baseline | 5.34 | 0.0002 | 8.0 | 0% | Câu trả lời dạng checklist khá tốt, nhưng thiếu traceability. |
| Production guardrails | multi-agent | 24.47 | 0.0013 | 8.0 | 100% | Khả năng audit tốt nhất nhờ có source, route history và critic review. |

## Nhận Xét Chất Lượng

- Baseline luôn nhanh hơn và rẻ hơn, đặc biệt với câu hỏi ngắn, vì chỉ dùng một lần gọi model và bỏ qua bước retrieval/analysis orchestration.
- Multi-agent tạo ra artifact để kiểm tra tốt hơn một cách ổn định: danh sách source, `research_notes`, `analysis_notes`, `route_history`, `trace` local và `critic_notes`.
- Bằng chứng thuyết phục nhất cho peer review đến từ truy vấn GraphRAG, vì workflow vừa giữ được references vừa mở ra đầy đủ các bước handoff.
- Artifact trace local được lưu tại `reports/trace_screenshot.png`, `reports/multi_agent_trace_example.json` và `reports/benchmark_results.json`.

## Failure Modes Và Cách Khắc Phục

- Search snippet yếu hoặc nhiễu:
  Tavily trả về một số đoạn trích dài hoặc kiểu bài blog, có thể làm `analysis_notes` bị loãng. Cách giảm thiểu: giới hạn độ dài snippet và ưu tiên xếp hạng domain đáng tin cậy.
- Độ trễ cao ở multi-agent:
  Hai lần gọi LLM của analyst và writer chiếm phần lớn thời gian chạy. Cách giảm thiểu: rút gọn prompt, cắt ngắn source snippet hoặc bỏ qua bước analysis cho truy vấn quá đơn giản.
- Nguồn có tính marketing hoặc là nguồn thứ cấp:
  Một số kết quả đến từ blog hoặc trang marketing. Cách giảm thiểu: thêm bộ lọc source và kiểm tra trích dẫn chặt hơn trong researcher/critic.
- Độ toàn vẹn của references:
  Lần chạy này critic pass vì writer luôn sinh ra mục `References:`. Nếu mục này bị thiếu, `CriticAgent` sẽ fail review và ghi lỗi vào state.

## Exit Ticket Draft

1. Nên dùng multi-agent khi task cần tách retrieval, analysis và writing để dễ debug và dễ kiểm soát chất lượng.
2. Không nên dùng multi-agent khi query ngắn, thời gian phản hồi quan trọng hơn, hoặc coordination overhead lớn hơn giá trị mang lại.
