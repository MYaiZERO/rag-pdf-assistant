## 2026-05-27 Summary 接口超时问题

问题：
调用 /summary 总结长 PDF 时出现 openai.APITimeoutError。

原因：
文档被分成多个 batch，每个 batch 都需要调用一次 LLM，整体耗时较长。

解决：
1. 在 OpenAI client 中设置 timeout=90
2. summary 增加 max_batches 参数，便于小规模测试
3. 对每个 batch 的 LLM 调用增加 try-except
4. 如果最终汇总失败，返回 partial_summaries，避免接口直接 500