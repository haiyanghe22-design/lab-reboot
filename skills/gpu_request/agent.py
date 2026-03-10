from openai import OpenAI
import json
import sys
sys.path.append('../..')
import config

client = OpenAI(api_key=config.DEEPSEEK_API_KEY, base_url=config.DEEPSEEK_BASE_URL)

SKILL_PROMPT = """你是GPU资源管理助手，负责理解用户的GPU请求需求。

支持的操作：
1. query_status - 查询GPU资源状态
2. submit_request - 提交GPU排队请求
3. confirm_usage - 确认使用GPU（需要request_id）
4. complete_request - 完成GPU使用（需要request_id）

返回JSON格式：
{
  "action": "操作类型",
  "gpu_count": 1,  // 仅submit_request需要
  "request_id": null,  // confirm_usage和complete_request需要
  "description": ""  // 可选的任务描述
}
"""

def parse_query(user_query):
    response = client.chat.completions.create(
        model=config.DEEPSEEK_MODEL,
        messages=[
            {"role": "system", "content": SKILL_PROMPT},
            {"role": "user", "content": f"用户问题: {user_query}\n\n请生成操作参数(JSON格式):"}
        ],
        response_format={"type": "json_object"}
    )

    return json.loads(response.choices[0].message.content)
