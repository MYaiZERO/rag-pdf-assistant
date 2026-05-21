from app.vector_store import vector_store
from app.llm import chat_with_llm

def build_rag_prompt (question:str,contexts:list[str]) -> str:
  """
  把检索到的资料和用户问题拼成一个prompt
  """
  context_text="\n\n".join(contexts)

  prompt= f"""
你是一个知识库问答助手。
请你只根据下面提供的资料回答用户问题。
如果资料中没有答案，请回答：根据已上传资料，我暂时无法确定。

【资料】
{context_text}

【用户问题】
{question}

【回答要求】
1. 用中文回答。
2. 回答要准确、简洁。
3. 不要编造资料中没有的信息。
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

  return {
    "question":question,
    "answer":answer,
    "contexts":contexts
  }
