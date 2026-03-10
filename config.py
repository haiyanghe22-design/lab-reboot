import os

PORT = 8000
HOST = "0.0.0.0"
SEARCH_PATHS = ["/home", "/data"]

GLM_API_KEY = os.getenv("GLM_API_KEY")
GLM_BASE_URL = "https://open.bigmodel.cn/api/paas/v4"
GLM_MODEL = "glm-4.7"

DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
DEEPSEEK_BASE_URL = "https://api.deepseek.com"
DEEPSEEK_MODEL = "deepseek-chat"

FEISHU_APP_ID = os.getenv("FEISHU_APP_ID")
FEISHU_APP_SECRET = os.getenv("FEISHU_APP_SECRET")

# 监控配置
MONITOR_USER_ID = os.getenv("MONITOR_USER_ID")
DISK_THRESHOLD = 90 #报警的磁盘阈值
DISK_CHECK_TIME = "00:00" #服务器时间
