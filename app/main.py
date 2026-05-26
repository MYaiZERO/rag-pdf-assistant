import os
import shutil
from typing import Optional

from fastapi import FastAPI,UploadFile,File
from app.llm import chat_with_llm
from app.pdf_loader import load_pdf_pages
from app.text_splitter import split_text
from app.vector_store import vector_store
from app.rag import answer_with_rag,answer_with_rag_debug
from app.document_summary import list_documents,summarize_document


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
def ask(question:str,top_k:int=3):
  """ 
  知识库问答接口，走RAG

  参数:
  question: 用户问题
  top_k: 检索最相关的前 k 个 chunk，默认是 3
  """
  result=answer_with_rag(
    question=question,
    top_k=top_k
    )
  return result

@app.get("/debug/ask")
def debug_ask(question:str,top_k:int=5):
  """
  RAG 调试接口。

  这个接口会返回：
  1. 大模型回答
  2. 引用来源 sources
  3. 检索到的完整 chunks
  4. 每个 chunk 的相似度分数
  5. 最终传给 LLM 的 prompt

  用途:
  调试 RAG 效果
  分析回答错误原因
  后续做前端可视化
  后续做自动评测
  """
  result=answer_with_rag_debug(
    question=question,
    top_k=top_k
  )

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

@app.get("/documents")
def documents():
  """
  查看当前知识库里有哪些文档

  这个接口的作用：
  1. 前端可以用它展示文档列表
  2. 用户可以知道 /summary 应该传哪个 filename
  """
  return {
    "documents":list_documents()
  }

@app.get("/summary")
def summary(filename:Optional[str]=None,batch_size:int=8,max_batches:Optional[int]=None):
  """
  文档摘要接口。

  参数:
  filename: 要总结的 PDF 文件名
  batch_size: 每次摘要多少个 chunk，默认 8
  max_batches: 最多处理多少批，用于测试或避免长文档超时

  如果知识库里只有一个文档，可以不传 filename
  如果有多个文档，必须指定 filename
  """
  documents=list_documents()

  if not documents:
    return {
      "message": "当前知识库还没有文档，请先上传 PDF。",
      "documents": []
    }
  
  if filename is None:
    if len(documents)==1:
      filename=documents[0]

    else:
      return{
        "message":"当前知识库有多个文档，请指定filename",
        "documents":documents
      }
    
  result=summarize_document(
    filename=filename,
    batch_size=batch_size,
    max_batches=max_batches
  )

  return result