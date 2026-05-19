from fastapi import FastAPI

app=FastAPI()

@app.get("/")
def home():
  return {
    "message":"RAG AI system is running"
  }

@app.get("/hello")
def hello():
  return {
    "reply":"Hello AI Engineer"
  }