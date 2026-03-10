from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from langchain_core.messages import HumanMessage
from langchain_core.tools import StructuredTool
from langchain_openai import ChatOpenAI
from graph_state import AgentState
from skill_loader import SkillLoader
import config

skill_loader = SkillLoader()
skill_loader.load_skill_metadata()

def create_tools():
    tools = []
    for skill_name, skill_info in skill_loader.skills.items():
        metadata = skill_info["metadata"]

        def make_func(name):
            def func(**kwargs):
                handler = skill_loader.load_handler(name)
                return getattr(handler, name)(**kwargs)
            return func

        tool = StructuredTool(
            name=skill_name,
            description=metadata["description"],
            func=make_func(skill_name),
            args_schema=metadata.get("parameters")
        )
        tools.append(tool)
    return tools

SYSTEM_PROMPT = """你是一个服务器管理助手，负责帮助用户查询和管理服务器资源。

你可以查询：CPU、内存、GPU显卡、磁盘、网络、进程等资源使用情况。
你可以管理：GPU排队请求、资源分配等。

当前用户信息：
- user_id: {user_id}
- user_name: {user_name}

重要规则：
1. 根据用户问题精确选择工具，避免调用不必要的工具
2. 如果用户只问显卡/GPU状态，只调用 get_resources
3. 如果用户只问磁盘，只调用 get_disk_usage
4. 如果用户问文件搜索，只调用 search_files
5. 如果用户要申请/使用GPU，调用 gpu_request，action=submit_request，自动使用当前用户的user_id和user_name
6. 用简洁清晰的语言回答，突出关键信息
"""

tools = create_tools()
llm = ChatOpenAI(
    api_key=config.DEEPSEEK_API_KEY,
    base_url=config.DEEPSEEK_BASE_URL,
    model=config.DEEPSEEK_MODEL
).bind_tools(tools)

def agent_node(state: AgentState):
    from langchain_core.messages import SystemMessage
    system_prompt = SYSTEM_PROMPT.format(
        user_id=state.get("user_id", "unknown"),
        user_name=state.get("user_name", "未知用户")
    )
    messages = [SystemMessage(content=system_prompt)] + list(state["messages"])
    response = llm.invoke(messages)
    return {"messages": [response]}

def should_continue(state: AgentState):
    last_message = state["messages"][-1]
    if not hasattr(last_message, "tool_calls") or not last_message.tool_calls:
        return "end"
    return "continue"

tool_node = ToolNode(tools)

workflow = StateGraph(AgentState)
workflow.add_node("agent", agent_node)
workflow.add_node("tools", tool_node)
workflow.set_entry_point("agent")
workflow.add_conditional_edges("agent", should_continue, {"continue": "tools", "end": END})
workflow.add_edge("tools", "agent")

graph = workflow.compile()

# 会话上下文存储
session_contexts = {}

def clean_markdown(text: str) -> str:
    import re
    text = re.sub(r'^#{1,6}\s+', '', text, flags=re.MULTILINE)
    text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)
    text = re.sub(r'\*(.+?)\*', r'\1', text)
    text = re.sub(r'`(.+?)`', r'\1', text)
    return text

def chat(user_message: str, user_id: str = "default", user_name: str = ""):
    if user_id not in session_contexts:
        session_contexts[user_id] = []

    session_contexts[user_id].append(HumanMessage(content=user_message))

    result = graph.invoke({
        "messages": session_contexts[user_id].copy(),
        "user_query": user_message,
        "user_id": user_id,
        "user_name": user_name
    })

    session_contexts[user_id].append(result["messages"][-1])
    response = result["messages"][-1].content
    return clean_markdown(response)

def clear_session(user_id: str = "default"):
    if user_id in session_contexts:
        session_contexts.pop(user_id)
