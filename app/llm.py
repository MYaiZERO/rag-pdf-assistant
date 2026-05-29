from openai import OpenAI

from app.config import (
  API_KEY,
  BASE_URL,
  MODEL,
  TIMEOUT
)

# 创建客户端
client=OpenAI(
  api_key=API_KEY,
  base_url=BASE_URL,
  timeout=TIMEOUT
)

def chat_with_llm(
  message:str,
  temperature:float=0.3,
  max_tokens:int=1000
):
  """
  调用大模型生成回答
  """

  response=client.chat.completions.create(
    model=MODEL,

    messages=[
      {
        "role":"system",
        "content":"你是一个严谨可靠的AI学习助手"
      },
      {
        "role":"user",
        "content":message
      }
    ],

    temperature=temperature,
    max_tokens=max_tokens
  )

  return response.choices[0].message.content