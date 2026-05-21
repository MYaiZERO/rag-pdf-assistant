import faiss
import numpy as np
from app.embeddings import embed_texts

class VectorStore:
  def __init__(self):
    self.index=None #保存 FAISS 索引
    self.chunks=[]

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

vector_store=VectorStore()