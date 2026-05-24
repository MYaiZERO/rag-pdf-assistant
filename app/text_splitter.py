def split_text(text:str,chunk_size:int=500,overlap:int=30) -> list[str]:
  """
  把长文本切分成多个小块chunk

  chunk_size:每块大约多少字符
  overlap:相邻chunk之间重叠多少字符，防止上下文断裂
  """

  if overlap >= chunk_size:
    raise ValueError(
      "overlap必须小于chunk_size"
    )
  
  chunks=[]

  start=0

  while start < len(text):
    end=start+chunk_size

    if end <len(text):
      split_pos=text.rfind(
        "\n",
        start,
        end
      )

      if split_pos==-1:
        split_pos=text.rfind(
          "。",
          start,
          end
        )

      if split_pos !=-1:
        end=split_pos

    chunk=text[start:end].strip()

    if chunk:
      chunks.append(chunk)

    start=max(
      end-overlap,
      start+1
    )

  return chunks
  # text_length=len(text)

  # while start < text_length:
  #   end=start+chunk_size
  #   chunk=text[start:end]

  #   if chunk.strip(): #如果这一块不是空白内容，就保存它
  #     chunks.append(chunk.strip())

  #   start=end-overlap

  # return chunks