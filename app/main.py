from fastapi import FastAPI
from app.llm import chat_with_llm

app=FastAPI()

@app.get("/")
def home():
  return {
    "message":"RAG AI system is running"
  }

@app.get("/chat")
def chat(message:str):
  reply=chat_with_llm(message)

  return {
    "question":message,
    "answer":reply
  }

# @app.get("/hello")
# def hello():
#   return {
#     "reply":"Hello AI Engineer"
#   }