from app.vector_store import vector_store
from app.llm import chat_with_llm

def list_documents()->list[str]:
  """
  返回当前知识库已经上传过的文档名称

  优先使用 vector_store.processed_files。
  如果 processed_files 为空，则从 chunks 的 metadata 中反推文档列表。
  """
  if vector_store.processed_files:
    return sorted(
      list(vector_store.processed_files)
    )
  
  documents=set()

  for chunk in vector_store.chunks:
    metadata=chunk.get(
      "metadata",
      {}
    )

    source=metadata.get("source")

    if source:
      documents.add(source)

  return sorted(
    list(documents)
  )

def get_document_chunks(filename:str)->list[dict]:
  """
  根据文件名，从向量库中取出属于该文档的所有 chunks。

  参数:
  filename: PDF 文件名

  返回:
  该 PDF 对应的 chunk 列表
  """
  document_chunks=[]

  for chunk in vector_store.chunks:
    metadata=chunk.get(
      "metadata",
      {}
    )

    if metadata.get("source")==filename:
      document_chunks.append(chunk)

  document_chunks.sort(
    key=lambda item:(
      item.get("metadata",{}).get("page",0),
      item.get("metadata",{}).get("chunk_id",0)
    )
  )

  return document_chunks

def split_chunks_into_batches(
    chunks:list[dict],
    batch_size:int=8
)->list[list[dict]]:
  """
  把文档 chunks 分成多个 batch。

  为什么要分批？
  因为长文档一次性塞给大模型，可能会超过上下文长度。
  分批摘要可以降低 token 压力。
  """
  batches=[]

  for i in range(0,len(chunks),batch_size):
    batches.append(chunks[i:i+batch_size])

  return batches

def build_batch_summary_prompt(
    filename:str,
    batch:list[dict],
    batch_index:int
)->str:
  """
  构造“局部摘要”的 prompt。

  每个 batch 只总结一部分 chunk。
  """
  content_parts=[]

  for item in batch:
    text=item["text"]
    metadata=item["metadata"]

    page=metadata.get(
      "page",
      "未知页码"
    )

    content_parts.append(
      f"""
【页码】
{page}

【内容】
{text}
"""
    )

  content = "\n\n".join(content_parts)

  prompt = f"""
你是一个专业的文档摘要助手。
现在需要你总结一个长文档中的一部分内容。

要求：
1. 只能根据给定内容总结
2. 不要编造没有出现的信息
3. 用中文回答
4. 提炼主要概念、关键观点和知识点
5. 保留重要术语
6. 不要写得太长

【文档名称】
{filename}

【当前部分编号】
第 {batch_index + 1} 部分

【文档内容】
{content}

请总结这一部分内容。
"""

  return prompt

def build_final_summary_prompt(
    filename:str,
    partial_summaries:list[str]
)->str:
  """
  构造“最终总摘要”的 prompt。

  输入是前面每个 batch 的局部摘要。
  输出是整个文档的结构化摘要。
  """

  partial_text=""

  for index, summary in enumerate(partial_summaries):
    partial_text += f"""
【第 {index + 1} 部分摘要】
{summary}
"""

  prompt = f"""
你是一个专业的文档总结助手。
下面是一个 PDF 文档被分段总结后的多个部分摘要。
请你综合这些摘要，生成整个文档的总摘要。

要求：
1. 用中文回答
2. 不要编造未出现的信息
3. 输出结构清晰
4. 适合给没有读过文档的人快速理解
5. 如果文档像课件，请总结它主要讲授了哪些知识点

请按下面结构输出：

## 文档主题
用 1-2 句话说明这个文档主要讲什么。

## 核心内容
用条目总结主要内容。

## 关键概念
列出文档中的重要概念或术语。

## 学习价值
说明读完这个文档可以理解什么。

【文档名称】
{filename}

【分段摘要】
{partial_text}
"""

  return prompt

def summarize_document(
    filename:str,
    batch_size:int=8,
    max_batches:int | None=None
)->dict:
  """
  对指定文档生成摘要。

  流程：
  1. 取出该文档的所有 chunks
  2. 分批生成局部摘要
  3. 汇总局部摘要，生成最终总摘要
  """
  chunks=get_document_chunks(filename)

  if not chunks:
    return {
      "filename":filename,
      "summary":"",
      "message":"没有找到这个文档，检查文档名是否正确",
      "chunks_count":0,
      "partial_summaries":[]
    }
  
  batches=split_chunks_into_batches(
    chunks,
    batch_size=batch_size
  )

  # 如果设置了 max_batches，就只处理前 max_batches 批
  # 这对于长 PDF 很重要，可以避免一次请求时间过长
  if max_batches is not None:
    batches = batches[:max_batches]

  partial_summaries = []
  failed_batches = []

  for batch_index, batch in enumerate(batches):
    prompt = build_batch_summary_prompt(
      filename=filename,
      batch=batch,
      batch_index=batch_index
    )

    try:
      partial_summary = chat_with_llm(
        prompt,
        temperature=0.2,
        max_tokens=700
      )

      partial_summaries.append(partial_summary)

    except Exception as e:
      # 某一批失败时，不让整个 summary 接口直接崩掉
      # 记录失败信息，继续处理后面的 batch
      failed_batches.append({
        "batch_index": batch_index,
        "error": str(e)
      })

  if not partial_summaries:
    return {
      "filename": filename,
      "summary": "",
      "message": "所有分批摘要都失败了，请检查模型服务或网络连接。",
      "chunks_count": len(chunks),
      "batches_count": len(batches),
      "batch_size": batch_size,
      "failed_batches": failed_batches,
      "partial_summaries": []
    }

  final_prompt = build_final_summary_prompt(
    filename=filename,
    partial_summaries=partial_summaries
  )

  try:
    final_summary = chat_with_llm(
      final_prompt,
      temperature=0.2,
      max_tokens=1200
    )

  except Exception as e:
    # 如果最终汇总失败，就先返回局部摘要
    # 这样至少用户能看到一部分结果，而不是 500
    return {
      "filename": filename,
      "summary": "",
      "message": "分段摘要已生成，但最终汇总失败。",
      "error": str(e),
      "chunks_count": len(chunks),
      "batches_count": len(batches),
      "batch_size": batch_size,
      "failed_batches": failed_batches,
      "partial_summaries": partial_summaries
    }

  return {
    "filename": filename,
    "summary": final_summary,
    "chunks_count": len(chunks),
    "batches_count": len(batches),
    "batch_size": batch_size,
    "max_batches": max_batches,
    "failed_batches": failed_batches,
    "partial_summaries": partial_summaries
  }