import os
import fnmatch
from datetime import datetime
from typing import List, Dict, Optional

def search_files(
    path: Optional[str] = None,
    name_pattern: Optional[str] = None,
    file_type: Optional[str] = None,
    min_size_mb: Optional[float] = None,
    max_size_mb: Optional[float] = None,
    max_results: int = 100,
    max_depth: Optional[int] = 3,
    include_dirs: bool = False
) -> Dict:
    import config
    if path:
        search_paths = path if isinstance(path, list) else [path]
    else:
        search_paths = config.SEARCH_PATHS
    results = []

    for base_path in search_paths:
        if not os.path.exists(base_path):
            continue

        for root, dirs, files in os.walk(base_path):
            if max_depth is not None:
                depth = root[len(base_path):].count(os.sep)
                if depth >= max_depth:
                    dirs.clear()

            if len(results) >= max_results:
                break

            # 搜索目录
            if include_dirs and name_pattern:
                for dir_name in dirs:
                    if len(results) >= max_results:
                        break
                    if fnmatch.fnmatch(dir_name.lower(), name_pattern.lower()):
                        full_path = os.path.join(root, dir_name)
                        try:
                            stat = os.stat(full_path)
                            results.append({
                                "path": full_path,
                                "filename": dir_name,
                                "directory": root,
                                "size_mb": 0,
                                "modified_time": datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S'),
                                "type": "directory"
                            })
                        except:
                            pass

            for file in files:
                if len(results) >= max_results:
                    break

                # 文件名模式匹配
                if name_pattern and not fnmatch.fnmatch(file.lower(), name_pattern.lower()):
                    continue

                # 文件类型匹配
                if file_type and not file.lower().endswith(f'.{file_type.lower()}'):
                    continue

                full_path = os.path.join(root, file)
                try:
                    stat = os.stat(full_path)
                    size_mb = stat.st_size / (1024**2)

                    # 大小过滤
                    if min_size_mb is not None and size_mb < min_size_mb:
                        continue
                    if max_size_mb is not None and size_mb > max_size_mb:
                        continue

                    results.append({
                        "path": full_path,
                        "filename": file,
                        "directory": root,
                        "size_mb": round(size_mb, 2),
                        "modified_time": datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S')
                    })
                except:
                    pass

    # 统计信息
    total_size = sum(r['size_mb'] for r in results)
    file_types = {}
    for r in results:
        ext = os.path.splitext(r['filename'])[1].lower()
        file_types[ext] = file_types.get(ext, 0) + 1

    return {
        "files": results,
        "total_count": len(results),
        "total_size_mb": round(total_size, 2),
        "file_types_distribution": file_types,
        "truncated": len(results) >= max_results
    }

