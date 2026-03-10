from openai import OpenAI
import json
import sys
sys.path.append('../..')
import config

client = OpenAI(api_key=config.DEEPSEEK_API_KEY, base_url=config.DEEPSEEK_BASE_URL)

SKILL_PROMPT = """你是资源监控助手，负责理解用户的资源查询需求，并生成合适的参数。

参数生成规则：
1. include_top_processes: 是否需要进程信息
   - 如果用户问"哪些进程占用高"、"top进程"等，设为 true
   - 如果只问整体资源情况，可设为 false 节省开销
   - 默认 true

2. top_n: 返回前N个进程
   - 通常 5 个足够
   - 如果用户明确要求更多，可设为 10

只返回 JSON 格式的参数，不要其他内容。
"""

def parse_query(user_query):
    response = client.chat.completions.create(
        model=config.DEEPSEEK_MODEL,
        messages=[
            {"role": "system", "content": SKILL_PROMPT},
            {"role": "user", "content": f"用户问题: {user_query}\n\n请生成查询参数(JSON格式):"}
        ],
        response_format={"type": "json_object"}
    )

    return json.loads(response.choices[0].message.content)
