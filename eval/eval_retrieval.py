import json
import os
import sys

# 把项目根目录加入 Python 搜索路径
# 这样在 eval/ 目录下运行脚本时，也能正常 import app.xxx
CURRENT_DIR=os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT=os.path.dirname(CURRENT_DIR)

if PROJECT_ROOT not in sys.path:
  sys.path.append(PROJECT_ROOT)

from app.vector_store import vector_store

def load_eval_questions(file_path:str)->list[dict]:
  """
  加载评测问题集

  参数:
  file_path: questions.json 的路径

  返回:
  一个问题列表，每个问题包含 question、expected_source、expected_pages
  """
  with open(file_path,"r",encoding="utf-8")as f:
    questions=json.load(f)

  return questions

def is_hit(
    retrieved_results:list[dict],
    expected_source:str,
    expected_pages:list[int]
)->bool:
  """
  判断检索结果是否命中标准答案页面。

  命中条件:
  1. 检索结果来自 expected_source
  2. 检索结果的 page 在 expected_pages 里面

  只要 top-k 里有一个结果满足，就算命中。
  """

  for item in retrieved_results:
    metadata=item.get(
      "metadata",
      {}
    )

    source=metadata.get("source")
    page=metadata.get("page")

    if source==expected_source and page in expected_pages:
      return True
    
  return False

def get_hit_rank(
    retrieved_results:list[dict],
    expected_source:str,
    expected_pages:list[int]
)->int |None:
  """
  返回正确结果第一次出现的位置。

  例如:
  - 第 1 个检索结果就命中，返回 1
  - 第 3 个检索结果才命中，返回 3
  - 没有命中，返回 None

  这个函数用于计算 MRR。
  """
  for index,item in enumerate(retrieved_results):
    metadata=item.get(
      "metadata",
      {}
    )

    source=metadata.get("source")
    page=metadata.get("page")

    if source==expected_source and page in expected_pages:
      return index+1
    
  return None

def evaluate_retrieval(
    questions:list[dict],
    top_k:int=3
)->dict:
  """
  执行检索评测。

  参数:
  questions: 测试问题列表
  top_k: 每个问题检索前几个 chunk

  返回:
  评测结果，包括命中数量、Hit@k、MRR 和每道题详情。
  """
  total=len(questions)
  hit_count=0
  reciprocal_ranks=[]
  details=[]

  for item in questions:
    question=item["question"]
    expected_source=item["expected_source"]
    expected_pages=item["expected_pages"]

    retrieved_results=vector_store.search(
      query=question,
      top_k=top_k
    )

    hit=is_hit(
      retrieved_results=retrieved_results,
      expected_source=expected_source,
      expected_pages=expected_pages
    )

    hit_rank=get_hit_rank(
      retrieved_results=retrieved_results,
      expected_source=expected_source,
      expected_pages=expected_pages
    )

    if hit:
      hit_count+=1

    if hit_rank is not None:
      reciprocal_ranks.append(
        1/hit_rank
      )
    else:
      reciprocal_ranks.append(0)

    retrieved_sources=[]

    for result in retrieved_results:
      metadata=result.get(
        "metadata",
        {}
      )

      retrieved_sources.append({
        "source":metadata.get("source"),
        "page":metadata.get("page"),
        "chunk_id":metadata.get("chunk_id"),
        "score":round(
          result.get("score",0),
          4
        )
      })

    details.append({
      "id":item.get("id"),
      "question":question,
      "expected_source":expected_source,
      "expected_pages":expected_pages,
      "hit":hit,
      "hit_rank":hit_rank,
      "retrieved":retrieved_sources
    })

  hit_rate=hit_count/total if total >0 else 0
  mrr=sum(reciprocal_ranks)/total if total >0 else 0

  return {
    "top_k": top_k,
    "total": total,
    "hit_count": hit_count,
    "hit_rate": hit_rate,
    "mrr": mrr,
    "details": details
  }

def print_report(result: dict):
  """
  在终端打印评测报告。
  """

  print("=" * 30)
  print("RAG 检索评测报告")
  print("=" * 30)

  print(f"Top K: {result['top_k']}")
  print(f"总问题数: {result['total']}")
  print(
    f"命中数量: {result['hit_count']} / {result['total']}"
  )
  print(
    f"Hit@{result['top_k']}: {result['hit_rate']:.2%}"
  )
  print(
    f"MRR: {result['mrr']:.4f}"
  )

  print("\n每道题详情:")
  print("-" * 30)

  for item in result["details"]:
    status = "命中" if item["hit"] else "未命中"

    print(f"\n[{status}] {item['id']}")
    print(f"问题: {item['question']}")
    print(f"标准页码: {item['expected_pages']}")
    print(f"命中位置: {item['hit_rank']}")

    print("检索结果:")
    for index, retrieved in enumerate(item["retrieved"]):
      print(
        f"  {index + 1}. "
        f"{retrieved['source']} "
        f"page={retrieved['page']} "
        f"chunk={retrieved['chunk_id']} "
        f"score={retrieved['score']}"
      )

def save_result(
  result: dict,
  output_path: str
):
  """
  把评测结果保存成 JSON 文件。

  这样后续可以把不同实验结果保存下来，
  用于 README 展示或者做对比。
  """

  with open(output_path, "w", encoding="utf-8") as f:
    json.dump(
      result,
      f,
      ensure_ascii=False,
      indent=2
    )


if __name__ == "__main__":
  questions_path = os.path.join(
    CURRENT_DIR,
    "questions.json"
  )

  questions = load_eval_questions(
    questions_path
  )

  # 你可以先测试 top_k=3
  result_top3 = evaluate_retrieval(
    questions=questions,
    top_k=3
  )

  print_report(result_top3)

  output_path = os.path.join(
    CURRENT_DIR,
    "retrieval_eval_top3.json"
  )

  save_result(
    result=result_top3,
    output_path=output_path
  )

  print(f"\n评测结果已保存到: {output_path}")