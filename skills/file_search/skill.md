# File Search

## name
search_files

## description
在指定路径下搜索文件，支持按文件名、类型、大小等条件筛选。返回匹配文件的路径、大小、修改时间等信息。

参数选择指导：
- path: 仔细分析用户问题，推断具体搜索路径。例如"hehy目录下"指/home/hehy或/data/hehy，"data目录"指/data
- name_pattern: 使用通配符进行模糊匹配，如"crossdock*"可匹配crossdock.tar.gz、crossdock2020等
- max_results: 根据查询目的设置，通常20-50足够，避免返回过多数据

## parameters
```json
{
  "type": "object",
  "properties": {
    "path": {
      "type": "string",
      "description": "搜索路径，默认为配置的搜索路径",
      "default": null
    },
    "name_pattern": {
      "type": "string",
      "description": "文件名模糊匹配（支持通配符*和?），如'*.pdb'、'crossdock*'",
      "default": null
    },
    "file_type": {
      "type": "string",
      "description": "文件扩展名（不含点），如'pdb'、'tar'、'gz'",
      "default": null
    },
    "min_size_mb": {
      "type": "number",
      "description": "最小文件大小（MB）",
      "default": null
    },
    "max_size_mb": {
      "type": "number",
      "description": "最大文件大小（MB）",
      "default": null
    },
    "max_results": {
      "type": "integer",
      "description": "最多返回结果数",
      "default": 100
    }
  }
}
```
