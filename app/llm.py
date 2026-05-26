import os 

from openai import OpenAI
from dotenv import load_dotenv

# 加载.env
load_dotenv()

# 创建客户端
client=OpenAI(
  api_key=os.getenv("API_KEY"),
  base_url=os.getenv("BASE_URL"),

  timeout=90
)

# 调用大模型
def chat_with_llm(message:str,temperature:float=0.3,max_tokens:int=1000):
  """
  调用大模型生成回答。

  参数:
  message: 传给大模型的用户内容
  temperature: 生成随机性，越低越稳定
  max_tokens: 限制模型最多输出多少 token，防止摘要过长或响应太慢
  """
  response=client.chat.completions.create(
    model=os.getenv("MODEL"),

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