# Resource Monitor

## name
get_resources

## description
获取服务器资源使用情况，包括CPU、内存、GPU显卡（NVIDIA）、系统负载、磁盘I/O、网络I/O以及资源占用最高的进程。可查询显卡使用率、显存占用、GPU温度等信息

## parameters
```json
{
  "type": "object",
  "properties": {
    "include_top_processes": {
      "type": "boolean",
      "description": "是否包含资源占用最高的进程列表",
      "default": true
    },
    "top_n": {
      "type": "integer",
      "description": "返回前N个资源占用最高的进程",
      "default": 5
    }
  }
}
```
