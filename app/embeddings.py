from sentence_transformers import SentenceTransformer

model=SentenceTransformer("BAAI/bge-small-zh-v1.5")

def embed_texts(texts:list[str]):
  """
  把多段文本转换成向量
  """
  embeddings=model.encode(texts,normalize_embeddings=True)
  return embeddings

