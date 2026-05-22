import os
import shutil

from fastapi import FastAPI,UploadFile,File
from app.llm import chat_with_llm
from app.pdf_loader import load_pdf_text
from app.text_splitter import split_text
from app.vector_store import vector_store
from app.rag import answer_with_rag

app=FastAPI()

@app.get("/")
def home():
  return {
    "message":"RAG AI system is running"
  }

@app.get("/chat")
def chat(message:str):
  """
  普通LLM聊天接口，不走知识库
  """
  reply=chat_with_llm(message)

  return {
    "question":message,
    "answer":reply
  }

@app.post("/upload")
async def upload_pdf(file:UploadFile=File(...)):
  """
  上传PDF，并把PDF内容加入知识库
  """
  os.makedirs("data",exist_ok=True)

  if vector_store.is_file_processed(file.filename):
    return{
      "filename":file.filename,
      "message":"这个PDF已经上传并处理过，不会重复加入知识库",
      "skipped":True,
      "status":vector_store.get_status()
    }

  file_path=f"data/{file.filename}"

  with open(file_path,"wb")as buffer:
    shutil.copyfileobj(file.file,buffer)

  text=load_pdf_text(file_path)

  if not text.strip():
    return {
      "filename":file.filename,
      "message":"PDF上传成功，但没有解析出文本，可能是扫描版PDF"
    }
  
  chunks=split_text(text)
  vector_store.add_texts(chunks)
  vector_store.mark_file_processed(file.filename)

  return {
    "filename":file.filename,
    "message":"PDF上传成功，已加入知识库",
    "skipped":False,
    "text_length":len(text),
    "chunks_count":len(chunks),
    "status":vector_store.get_status()
  }

@app.get("/ask")
def ask(question:str):
  """ 
  知识库问答接口，走RAG
  """
  result=answer_with_rag(question)
  return result

@app.get("/status")
def status():
  """
  查看知识库状态
  """
  return vector_store.get_status()