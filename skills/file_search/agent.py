from openai import OpenAI
import json
import sys
sys.path.append('../..')
import config

client = OpenAI(api_key=config.DEEPSEEK_API_KEY, base_url=config.DEEPSEEK_BASE_URL)

SKILL_PROMPT = """你是文件搜索助手，负责理解用户的文件搜索需求，并生成合适的搜索参数。

参数生成规则：
1. path: 从用户问题推断搜索路径（可以是字符串或数组）
   - "hehy目录" → ["/home/hehy", "/data/hehy"]
   - "data目录" → "/data"
   - 如果不确定，返回 null 使用默认路径

2. name_pattern: 文件名模糊匹配
   - 使用通配符 * 和 ?
   - 例如: "crossdock*" 匹配 crossdock.tar.gz、crossdock2020

3. file_type: 文件扩展名（不含点）
   - 例如: pdb, tar, gz

4. max_results: 根据查询目的设置
   - 检查是否存在: 10-20
   - 列出文件: 20-50
   - 详细统计: 50-100

5. max_depth: 目录遍历深度（从指定路径开始计算）
   - 默认为 3 层
   - 如果用户明确要求"深入搜索"或"完整搜索"，设置为 null（无限制）
   - 普通搜索保持默认值

6. include_dirs: 是否包含目录搜索
   - 如果用户问"有没有XX目录/文件夹"或搜索的是目录名，设置为 true
   - 默认为 false（仅搜索文件）

只返回 JSON 格式的参数，不要其他内容。
"""

def parse_query(user_query):
    response = client.chat.completions.create(
        model=config.DEEPSEEK_MODEL,
        messages=[
            {"role": "system", "content": SKILL_PROMPT},
            {"role": "user", "content": f"用户问题: {user_query}\n\n请生成搜索参数(JSON格式):"}
        ],
        response_format={"type": "json_object"}
    )

    return json.loads(response.choices[0].message.content)
