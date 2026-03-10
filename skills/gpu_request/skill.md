# GPU Request

## name
gpu_request

## description
GPU资源管理：查询GPU状态、提交排队请求、确认使用、完成释放

## parameters
```json
{
  "type": "object",
  "properties": {
    "action": {
      "type": "string",
      "enum": ["query_status", "submit_request", "confirm_usage", "complete_request"],
      "description": "操作类型"
    },
    "user_id": {
      "type": "string",
      "description": "用户ID（submit_request需要）"
    },
    "user_name": {
      "type": "string",
      "description": "用户名（submit_request可选）"
    },
    "gpu_count": {
      "type": "integer",
      "default": 1,
      "description": "GPU数量（submit_request可选）"
    },
    "request_id": {
      "type": "integer",
      "description": "任务ID（confirm_usage和complete_request需要）"
    },
    "description": {
      "type": "string",
      "description": "任务描述（submit_request可选）"
    }
  },
  "required": ["action"]
}
```
