from pypdf import PdfReader

def load_pdf_text(file_path:str) -> str:
  """
  读取PDF文件，提取里面的文字
  """
  reader=PdfReader(file_path)

  all_text=[]

  for page in reader.pages:
    text=page.extract_text()
    if text:
      all_text.append(text)

  return "\n".join(all_text)