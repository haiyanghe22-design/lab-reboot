import psutil
import subprocess

def get_cpu_info():
    return {
        "usage_percent": psutil.cpu_percent(interval=1),
        "count": psutil.cpu_count(),
        "load_average": psutil.getloadavg()
    }

def get_memory_info():
    mem = psutil.virtual_memory()
    swap = psutil.swap_memory()
    return {
        "total_gb": round(mem.total / (1024**3), 2),
        "used_gb": round(mem.used / (1024**3), 2),
        "available_gb": round(mem.available / (1024**3), 2),
        "percent": mem.percent,
        "swap_total_gb": round(swap.total / (1024**3), 2),
        "swap_used_gb": round(swap.used / (1024**3), 2),
        "swap_percent": swap.percent
    }

def get_gpu_info():
    try:
        result = subprocess.run(['nvidia-smi', '--query-gpu=index,name,memory.used,memory.total,utilization.gpu,temperature.gpu',
                               '--format=csv,noheader,nounits'],
                              capture_output=True, text=True, timeout=5)
        if result.returncode != 0:
            return []

        gpus = []
        for line in result.stdout.strip().split('\n'):
            if line:
                parts = line.split(', ')
                gpus.append({
                    "index": int(parts[0]),
                    "name": parts[1],
                    "memory_used_mb": int(parts[2]),
                    "memory_total_mb": int(parts[3]),
                    "utilization_percent": int(parts[4]),
                    "temperature_c": int(parts[5]) if len(parts) > 5 else None
                })
        return gpus
    except:
        return []

def get_io_info():
    disk_io = psutil.disk_io_counters()
    net_io = psutil.net_io_counters()
    return {
        "disk": {
            "read_mb": round(disk_io.read_bytes / (1024**2), 2),
            "write_mb": round(disk_io.write_bytes / (1024**2), 2)
        },
        "network": {
            "sent_mb": round(net_io.bytes_sent / (1024**2), 2),
            "recv_mb": round(net_io.bytes_recv / (1024**2), 2)
        }
    }

def get_top_processes(top_n=5):
    processes = []
    for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
        try:
            processes.append(proc.info)
        except:
            pass

    processes.sort(key=lambda x: x['cpu_percent'] or 0, reverse=True)
    top_cpu = processes[:top_n]

    processes.sort(key=lambda x: x['memory_percent'] or 0, reverse=True)
    top_mem = processes[:top_n]

    return {
        "top_cpu": [{"pid": p['pid'], "name": p['name'], "cpu_percent": round(p['cpu_percent'] or 0, 2)} for p in top_cpu],
        "top_memory": [{"pid": p['pid'], "name": p['name'], "memory_percent": round(p['memory_percent'] or 0, 2)} for p in top_mem]
    }

def get_resources(include_top_processes=True, top_n=5):
    result = {
        "cpu": get_cpu_info(),
        "memory": get_memory_info(),
        "gpu": get_gpu_info(),
        "io": get_io_info()
    }

    if include_top_processes:
        result["top_processes"] = get_top_processes(top_n)

    return result
