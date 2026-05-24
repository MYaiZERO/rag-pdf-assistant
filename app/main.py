import os
import shutil

from fastapi import FastAPI,UploadFile,File
from app.llm import chat_with_llm
from app.pdf_loader import load_pdf_pages
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

  pages=load_pdf_pages(file_path)

  if not pages:
    return {
      "filename":file.filename,
      "message":"PDF上传成功，但没有解析出文本，可能是扫描版PDF"
    }
  
  all_chunks=[]
  all_metadata=[]

  total_text_length=0

  for page_idx,page_text in enumerate(pages):
    total_text_length+=len(page_text)

    chunks=split_text(page_text)

    for chunk_idx,chunk in enumerate(chunks):
      all_chunks.append(chunk)

      all_metadata.append({
        "source":file.filename,
        "page":page_idx+1,
        "chunk_id":chunk_idx
      })

  vector_store.add_texts(
    all_chunks,
    all_metadata
  )

  vector_store.mark_file_processed(
    file.filename
  )

  return {
    "filename":file.filename,
    "message":"PDF上传成功，已加入知识库",
    "skipped":False,
    "pages_count":len(pages),
    "text_length":total_text_length,
    "chunks_count":len(all_chunks),
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

@app.get("/source")
def get_sources():
  source_info=[]

  for chunk in vector_store.chunks:
    meta=chunk["metadata"]

    source_info.append({
      "source":meta.get(
        "source"
      ),

      "page":meta.get(
        "page"
      ),

      "chunk_id":meta.get(
        "chunk_id"
      )
    })
  return {
    "total_chunks":len(
      vector_store.chunks
    ),
    "sources":source_info
  }