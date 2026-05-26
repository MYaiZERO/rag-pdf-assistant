from app.vector_store import vector_store
from app.llm import chat_with_llm

def build_rag_prompt (question:str,contexts:list[dict]) -> str:
  """
  把检索到的资料和用户问题拼成一个prompt
  参数:
  question: 用户提出的问题
  contexts: 向量数据库检索出来的相关文本片段
  """
  context_parts=[]

  for item in contexts:
    text=item["text"]
    metadata=item["metadata"]

    source=metadata.get(
      "source",
      "未知文件"
    )

    page=metadata.get(
      "page",
      "未知页码"
    )

    chunk_id=metadata.get(
      "chunk_id",
      "未知chunk"
    )
    context_parts.append(
       f"""
【来源文件】
{source}

【页码】
{page}

【Chunk ID】
{chunk_id}

【内容】
{text}
"""
    )

  context_text="\n\n".join(context_parts)

  prompt= f"""
你是一个专业知识库问答助手。
严格依据提供资料回答。

要求：
1.只能使用资料中的信息
2.不允许编造
3.若资料不足，请明确回答：“根据已上传资料，我暂时无法确定。”
4.回答使用中文
5.回答尽量简洁准确
6.如果可以，请在回答中提到依据来自哪个文件或哪一页

【资料】
{context_text}

【用户问题】
{question}

"""
  return prompt

def build_sources(contexts:list[dict])-> list[dict]:
  """
  从检索结果中提取source信息

  """
  sources=[]

  for item in contexts:
    meta=item["metadata"]

    sources.append({
      "source":meta.get(
        "source",
        "未知文件"
      ),

      "page":meta.get(
        "page",
        "未知页码"
      ),

      "chunk_id":meta.get(
        "chunk_id",
        "未知chunk"
      ),

      "score":round(
        item["score"],
        4
      )
    })
  return sources

def answer_with_rag(question:str,top_k:int=3) -> dict:
  """
  RAG问答主流程：
  1.检索相关资料
  2.构造prompt
  3.调用LLM
  4.返回答案和引用来源

  参数:
  question: 用户问题
  top_k: 检索最相关的前 k 个 chunk
  """
  contexts=vector_store.search(question,top_k=top_k)

  if not contexts:
    return {
      "question":question,
      "answer":"当前知识库还没有内容，请先上传PDF",
      "sources":[],
      "contexts":[]
    }
  
  prompt=build_rag_prompt(question,contexts)
  answer=chat_with_llm(prompt)
  sources=build_sources(contexts)

  return {
    "question":question,
    "answer":answer,
    "sources":sources,
    "contexts":contexts
  }

def answer_with_rag_debug(question:str,top_k:int=5)->dict:
  """
  RAG调试版回答
  和 answer_with_rag 的区别：
  1. 返回最终 prompt
  2. 返回完整 retrieved_chunks
  3. 返回 top_k 参数
  4. 方便后续做 RAG 评测和前端调试页面

  这个接口主要用于开发、调试、面试展示，不一定直接给普通用户使用。
  """
  contexts=vector_store.search(
    question,
    top_k=top_k
  )

  if not contexts:
    return {
      "question":question,
      "answer":"当前知识库还没有内容，请先上传PDF",
      "top_k":top_k,
      "sources":[],
      "retrieved_chunks":[],
      "prompt":""
    }
  
  prompt=build_rag_prompt(
    question,
    contexts
  )
 
  answer=chat_with_llm(prompt)

  sources=build_sources(contexts)

  # retrieved_chunks 用于展示检索详情
  # 这里不直接叫 contexts，是为了让 debug 接口语义更清楚
  retrieved_chunks = []

  for item in contexts:
    retrieved_chunks.append({
      "text":item["text"],
      "metadata":item["metadata"],
      "score":round(
        item["score"],
        4
      )
    })

  return {
    "question":question,
    "answer":answer,
    "top_k":top_k,
    "sources":sources,
    "retrieved_chunks":retrieved_chunks,
    "prompt":prompt
  }