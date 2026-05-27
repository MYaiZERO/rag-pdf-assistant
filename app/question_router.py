def classify_question(question:str)->str:
  """
  判断用户问题属于哪一类。

  返回值:
  - "summary": 全局摘要类问题
  - "rag": 局部知识问答类问题

  为什么先用规则判断？
  1. 速度快
  2. 不消耗 LLM 调用次数
  3. 对“总结一下文档”这类问题已经足够稳定
  """

  question=question.strip()

  summary_keywords=[
    "讲了什么",
    "主要讲什么",
    "主要内容",
    "核心内容",
    "总结",
    "概括",
    "摘要",
    "梳理",
    "整体介绍",
    "大意",
    "全文",
    "整篇",
    "这个文档",
    "这份文档",
    "这个pdf",
    "这份pdf",
    "这篇文章",
    "这份资料"
  ]

  # 只要问题中出现这些关键词，就认为用户想要文档级总结
  for keyword in summary_keywords:
    if keyword in question:
      return "summary"
    
  short_summary_questions=[
    "文档内容",
    "这是什么",
    "介绍一下",
    "说一下"
  ]

  for keyword in short_summary_questions:
    if keyword in question and len(question)<=15:
      return "summary"
    
  return "rag"