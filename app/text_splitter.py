def split_text(text:str,chunk_size:int=500,overlap:int=100) -> list[str]:
  """
  把长文本切分成多个小块chunk

  chunk_size:每块大约多少字符
  overlap:相邻chunk之间重叠多少字符，防止上下文断裂
  """
  chunks=[]

  start=0
  text_length=len(text)

  while start < text_length:
    end=start+chunk_size
    chunk=text[start:end]

    if chunk.strip(): #如果这一块不是空白内容，就保存它
      chunks.append(chunk.strip())

    start=end-overlap

  return chunks