# config.py
import os
from dotenv import load_dotenv

# 加载 .env 文件
load_dotenv()

# AI 配置
LLM_API_KEY = os.getenv("LLM_API_KEY")
LLM_URL = os.getenv("LLM_URL", "https://api.groq.com/openai/v1/chat/completions")
MODEL_NAME = os.getenv("MODEL_NAME", "llama-3.3-70b-versatile")

# ActivityWatch 基础地址
AW_API_BASE = os.getenv("AW_API_BASE", "http://localhost:5600/api/0")

# 动态获取 settings.json 路径
# 优先读取 .env 中的路径，如果没有则使用默认的 Windows AppData 路径
default_settings_path = os.path.join(
    os.environ.get('LOCALAPPDATA', ''), 
    r"activitywatch\activitywatch\aw-server\settings.json"
)
SETTINGS_PATH = os.getenv("AW_SETTINGS_PATH", default_settings_path)

# 简单校验
if not LLM_API_KEY:
    raise ValueError("错误: 未在 .env 文件中找到 LLM_API_KEY")
