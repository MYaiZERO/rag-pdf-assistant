from sentence_transformers import SentenceTransformer

_model=None

def get_embedding_model():
  """
  懒加载embedding模型，第一次真正需要生成向量时才加载模型
  """
  global _model

  if _model is None:
    print("Loading embedding model...")
    _model=SentenceTransformer("BAAI/bge-small-zh-v1.5")
    print("Embedding model loaded")

  return _model


def embed_texts(texts:list[str]):
  """
  把多段文本转换成向量
  """
  model=get_embedding_model()
  embeddings=model.encode(texts,normalize_embeddings=True)
  return embeddings

