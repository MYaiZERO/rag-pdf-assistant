import faiss

import os
import pickle

import numpy as np
from app.embeddings import embed_texts

class VectorStore:
  def __init__(self):
    self.index=None #保存 FAISS 索引
    self.chunks=[]

    self.storage_dir="storage"
    self.index_path=os.path.join(self.storage_dir,"faiss.index")
    self.chunks_path=os.path.join(self.storage_dir,"chunks.pkl")

    self.load()

  def add_texts(self,chunks:list[str]):
    """
    把文本chunk生成向量，并存入FAISS
    """
    if not chunks:
      return 
    
    embeddings=embed_texts(chunks)
    embeddings=np.array(embeddings).astype("float32")

    dimension=embeddings.shape[1]

    if self.index is None:
      self.index=faiss.IndexFlatIP(dimension)

    self.index.add(embeddings)
    self.chunks.extend(chunks)

    self.save()

  def search(self,query:str,top_k:int=3) -> list[str]:
    """
    根据用户问题，检索最相关的文本chunk
    """
    if self.index is None or len(self.chunks)==0:
      return []
    
    query_embedding=embed_texts([query])
    query_embedding=np.array(query_embedding).astype("float32")

    scores,indices=self.index.search(query_embedding,top_k)

    results=[]

    for idx in indices[0]:
      if idx != -1:
        results.append(self.chunks[idx])

    return results
  
  def get_status(self) -> dict:
    """
    查看当前向量数据库状态
    """
    return {
      "index_loaded":self.index is not None,
      "chunks_count":len(self.chunks),
      "index_path":self.index_path,
      "chunks_path":self.chunks_path,
      "index_saved":os.path.exists(self.index_path),
      "chunks_saved":os.path.exists(self.chunks_path)
    }
  
  def save(self):
    """
    把FAISS index和chunks保存到本地
    """
    os.makedirs(self.storage_dir,exist_ok=True)

    if self.index is not None:
      faiss.write_index(self.index,self.index_path)

    with open(self.chunks_path,"wb") as f:
      pickle.dump(self.chunks,f)

  def load(self):
    """
    启动项目时，从本地加载FAISS index和chunks
    """
    if os.path.exists(self.index_path):
      self.index=faiss.read_index(self.index_path)

    if os.path.exists(self.chunks_path):
      with open(self.chunks_path,"rb") as f:
        self.chunks=pickle.load(f)

vector_store=VectorStore()