from pypdf import PdfReader

def load_pdf_pages(file_path:str) -> list[str]:
  """
  读取PDF文件，返回每一页文本
  """
  reader=PdfReader(file_path)

  pages=[]

  for page in reader.pages:
    text=page.extract_text()
    if text:
      pages.append(
        text.strip()
      )

  return pages