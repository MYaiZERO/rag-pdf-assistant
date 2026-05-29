import os
from dotenv import load_dotenv

# 加载 .env
load_dotenv()

# API配置
API_KEY=os.getenv("API_KEY")
BASE_URL=os.getenv("BASE_URL")
MODEL=os.getenv("MODEL")

# LLM参数
TIMEOUT=90