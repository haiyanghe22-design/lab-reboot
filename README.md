# Lab Manager - 实验室服务器管理 Agent

基于 LangGraph 的智能服务器管理助手，通过飞书机器人提供服务器资源查询和管理功能。

## 功能特性

- **资源监控**: 查询 CPU、内存、GPU、进程等实时使用情况
- **磁盘管理**: 查看磁盘使用情况和空间统计，定时检查磁盘告警
- **文件搜索**: 按关键词搜索服务器文件
- **GPU排队管理**: GPU资源申请、排队、自动分配、超时管理
- **飞书集成**: 通过飞书机器人与用户交互
- **智能对话**: 基于 LangGraph 的多轮对话和工具调用
- **定时任务**: 自动磁盘检查、GPU资源调度

## 技术架构

- **LangGraph**: 状态图管理对话流程
- **LangChain**: 工具封装和 LLM 集成
- **DeepSeek API**: 大语言模型推理
- **飞书开放平台**: 消息接收和发送

## 环境要求

- Python 3.10+
- Conda 环境管理器

## 安装步骤

### 1. 创建 Conda 环境

```bash
conda create -n lab-manager python=3.10
conda activate lab-manager
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 配置环境变量

在 `~/.bashrc` 或 `~/.zshrc` 中添加以下环境变量：

```bash
export GLM_API_KEY="your-glm-api-key"
export DEEPSEEK_API_KEY="your-deepseek-api-key"
export FEISHU_APP_ID="your-feishu-app-id"
export FEISHU_APP_SECRET="your-feishu-app-secret"
export MONITOR_USER_ID="your-monitor-user-id"
```

然后重新加载配置：
```bash
source ~/.bashrc
```

> 提示：查看 `config.py` 了解所需的环境变量

### 4. 获取 API 密钥

**DeepSeek API**:
1. 访问 https://platform.deepseek.com
2. 注册账号并创建 API Key
3. 复制 API Key 到 `config.py`

**飞书应用**:
1. 访问 https://open.feishu.cn/app
2. 创建企业自建应用
3. 获取 App ID 和 App Secret
4. 配置事件订阅和权限

## 启动服务

```bash
python feishu_longconn.py
```

启动后，机器人会连接飞书并开始监听消息。

## 使用示例

在飞书中向机器人发送消息：

**资源查询**
- "查询服务器资源"
- "显卡使用情况"
- "磁盘空间"

**文件搜索**
- "搜索文件 test.py"

**GPU管理**
- "我要用GPU" - 申请GPU资源
- "查询GPU状态" - 查看GPU使用情况
- "确认 1" - 确认使用GPU（任务ID为1）
- "完成任务 1" - 释放GPU资源

## 项目结构

```
labReboot/
├── agent.py              # LangGraph 主 Agent
├── graph_state.py        # 状态定义
├── skill_loader.py       # 技能加载器
├── feishu_longconn.py    # 飞书长连接
├── scheduler.py          # 定时任务调度器
├── gpu_queue.py          # GPU队列管理器
├── config.py             # 配置文件
├── skills/               # 技能模块
│   ├── resource_monitor/ # 资源监控
│   ├── disk_usage/       # 磁盘查询
│   ├── file_search/      # 文件搜索
│   ├── gpu_request/      # GPU排队管理
│   └── feishu_client.py  # 飞书客户端
├── sessions/             # 会话记录
└── gpu_queue.db          # GPU队列数据库
```

## 开发说明

### GPU排队管理机制

**工作流程：**
1. 用户申请GPU → 有空闲直接分配，无空闲加入排队
2. 定时检查（每2分钟）→ 处理超时、通知排队用户
3. 用户确认（5分钟内）→ 开始使用GPU
4. 使用完成 → 释放资源，通知下一位

**状态流转：**
- `pending` → 排队中
- `notified` → 已通知，等待确认（5分钟）
- `confirmed` → 已确认使用
- `timeout` → 超时未确认
- `completed` → 已完成

**配置参数：**
- `max_concurrent`: 最大并发GPU数量（默认4）
- 超时时间：5分钟
- 检查间隔：2分钟

### 添加新技能

1. 在 `skills/` 下创建技能目录
2. 添加 `metadata.json` 定义技能信息
3. 添加 `handler.py` 实现技能逻辑
4. 重启服务自动加载

### 技能示例

```json
{
  "name": "your_skill",
  "description": "技能描述",
  "version": "1.0.0"
}
```

## 许可证

MIT License
