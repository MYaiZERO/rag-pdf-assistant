# Development Notes

## 2026-05-25 Chunk 重复检索问题

### 问题
Top-k 检索结果出现大量重复内容。

### 原因
使用 overlap chunking：
chunk_size=50
overlap=100
导致相邻 chunk 高度重叠。
FAISS Top-k 易命中连续 chunk。

### 解决
1. overlap 调整
2. Search 增加简单去重逻辑
3. 调整 top_k 参数



## 2026-05-26 Metadata 升级

### 问题
RAG 检索结果无法定位来源页码。
所有 source.page 都显示为 1。

### 原因
PDF Loader 将整本 PDF 拼接成单个字符串：
load_pdf_text()导致页级信息丢失。

### 解决
1. 修改 PDF Loader：load_pdf_pages()
2. 返回：list[str]
3. 上传流程改为：
逐页 chunk → 逐页 metadata 生成。
4. metadata 新增：
* source
* page
* chunk_id



## 2026-05-27 Summary 接口超时问题

### 问题：
调用 /summary 总结长 PDF 时出现 openai.APITimeoutError。

### 原因：
文档被分成多个 batch，每个 batch 都需要调用一次 LLM，整体耗时较长。

### 解决：
1. 在 OpenAI client 中设置 timeout=90
2. summary 增加 max_batches 参数，便于小规模测试
3. 对每个 batch 的 LLM 调用增加 try-except
4. 如果最终汇总失败，返回 partial_summaries，避免接口直接 500



# 2026-05-29 requirements 自动生成问题（pipreqs）
## 问题1：pipreqs 生成失败（网络超时）
执行：
bash
pipreqs . --force

报错：
text
requests.exceptions.ConnectTimeout
HTTPSConnectionPool(host='pypi.python.org', port=443)
Connection timed out

### 原因
pipreqs 默认会联网访问 PyPI。
其工作流程大致为：
扫描项目 import
↓
查询 package mapping
↓
访问 pypi.python.org
↓
生成 requirements.txt

当前环境访问 PyPI 超时，因此生成失败。

### 解决方案
改用本地扫描模式：
bash
pipreqs . --force --use-local

避免联网查询。

### 收获
理解了：
- `pip freeze` → 当前环境完整快照
- `pipreqs` → 项目依赖扫描
很多工程工具默认存在网络依赖，需要考虑：
- 网络可用性
- 离线模式
- 本地依赖解析

## 问题2：pipreqs 依赖漏检问题
执行：
bash
pipreqs . --force --use-local

生成结果只有：
txt
faiss==1.14.1
sentence_transformers==5.3.0

### 原因

pipreqs 基于静态 import 扫描。
对某些 import 写法识别不稳定，例如：
```python
from fastapi import FastAPI
from openai import OpenAI
```
因此可能出现 requirements 不完整的问题。

### 解决方案
采用：
**自动生成 + 人工审核**流程。

先执行：
```bash
pipreqs . --force --use-local
```
再结合：
```bash
pip list
```
以及项目源码中的 import 手动检查依赖。

### 最终 requirements.txt

```txt
fastapi==0.128.0
uvicorn==0.40.0
openai==2.30.0
numpy==2.2.5
pypdf==6.8.0
sentence-transformers==5.3.0
faiss-cpu==1.14.1
python-multipart==0.0.22
```
