import shutil
from typing import Dict, List

def get_disk_usage() -> Dict:
    partitions = []
    total_size = 0
    total_used = 0

    with open('/proc/mounts', 'r') as f:
        for line in f:
            parts = line.split()
            device, mount_point, fstype = parts[0], parts[1], parts[2]

            if not device.startswith('/dev/') or fstype in ['tmpfs', 'devtmpfs']:
                continue

            try:
                usage = shutil.disk_usage(mount_point)
                size_gb = usage.total / (1024**3)
                used_gb = usage.used / (1024**3)
                free_gb = usage.free / (1024**3)
                used_percent = (usage.used / usage.total * 100) if usage.total > 0 else 0

                partitions.append({
                    "device": device,
                    "mount_point": mount_point,
                    "filesystem": fstype,
                    "total_gb": round(size_gb, 2),
                    "used_gb": round(used_gb, 2),
                    "free_gb": round(free_gb, 2),
                    "used_percent": round(used_percent, 2)
                })

                total_size += usage.total
                total_used += usage.used
            except:
                continue

    return {
        "partitions": partitions,
        "partition_count": len(partitions),
        "total_size_gb": round(total_size / (1024**3), 2),
        "total_used_gb": round(total_used / (1024**3), 2),
        "total_free_gb": round((total_size - total_used) / (1024**3), 2),
        "overall_used_percent": round((total_used / total_size * 100) if total_size > 0 else 0, 2)
    }
