from app.vector_store import vector_store
from app.llm import chat_with_llm

def build_rag_prompt (question:str,contexts:list[dict]) -> str:
  """
  把检索到的资料和用户问题拼成一个prompt
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

    context_parts.append(
       f"""
【来源文件】
{source}

【页码】
{page}

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

【资料】
{context_text}

【用户问题】
{question}

"""
  return prompt

def answer_with_rag(question:str) -> dict:
  """
  RAG问答主流程：
  1.检索相关资料
  2.构造prompt
  3.调用LLM
  """
  contexts=vector_store.search(question,top_k=3)

  if not contexts:
    return {
      "question":question,
      "answer":"当前知识库还没有内容，请先上传PDF",
      "contexts":[]
    }
  
  prompt=build_rag_prompt(question,contexts)
  answer=chat_with_llm(prompt)

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

      "score":round(
        item["score"],
        4
      )   
    })

  return {
    "question":question,
    "answer":answer,
    "sources":sources,
    "contexts":contexts
  }