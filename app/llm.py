import os 

from openai import OpenAI
from dotenv import load_dotenv

# 加载.env
load_dotenv()

# 创建客户端
client=OpenAI(
  api_key=os.getenv("API_KEY"),
  base_url=os.getenv("BASE_URL")
)

# 调用大模型
def chat_with_llm(message:str):
  response=client.chat.completions.create(
    model=os.getenv("MODEL"),

    messages=[
      {
        "role":"system",
        "content":"你是一个AI学习助手"
      },
      {
        "role":"user",
        "content":message
      }
    ],

    temperature=0.7
    
  )

  return response.choices[0].message.content