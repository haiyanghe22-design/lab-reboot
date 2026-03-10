from gpu_queue import GPUQueueManager

gpu_manager = GPUQueueManager(max_concurrent=4)

def gpu_request(action: str, user_id: str = "", user_name: str = "", gpu_count: int = 1, request_id: int = None, description: str = ""):
    """GPU资源管理统一入口"""
    if action == "query_status":
        return query_gpu_status()
    elif action == "submit_request":
        return submit_gpu_request(user_id, user_name, gpu_count, description)
    elif action == "confirm_usage":
        return confirm_gpu_usage(request_id)
    elif action == "complete_request":
        return complete_gpu_request(request_id)
    return "❌ 未知操作"

def query_gpu_status():
    """查询GPU资源状态"""
    status = gpu_manager.get_queue_status()
    return f"📊 GPU资源状态\n空闲: {status['available_slots']}/{gpu_manager.max_concurrent}\n排队: {status['pending']}人\n等待确认: {status['notified']}人\n使用中: {status['confirmed']}人"

def submit_gpu_request(user_id: str, user_name: str = "", gpu_count: int = 1, description: str = ""):
    """提交GPU排队请求"""
    status = gpu_manager.get_queue_status()

    if status['available_slots'] > 0:
        # 有空闲，直接分配为confirmed状态
        request_id = gpu_manager.add_request(user_id, user_name, gpu_count, description=description)
        # 直接更新为confirmed
        import sqlite3
        conn = sqlite3.connect(gpu_manager.db_path)
        conn.execute("UPDATE gpu_requests SET status='confirmed', confirmed_at=datetime('now') WHERE id=?", (request_id,))
        conn.commit()
        conn.close()
        return f"✅ GPU资源充足，已直接分配\n任务ID: {request_id}\n请开始使用GPU\n使用完成后请回复：完成任务 {request_id}"
    else:
        # 无空闲，加入排队
        request_id = gpu_manager.add_request(user_id, user_name, gpu_count, description=description)
        position = gpu_manager.get_queue_position(request_id)
        return f"⏳ GPU资源已满，已加入排队\n任务ID: {request_id}\n排队位置: 第{position}位\n有空闲时会通知您"

def confirm_gpu_usage(request_id: int):
    """确认使用GPU"""
    success = gpu_manager.confirm_request(request_id)
    if success:
        return f"✅ 确认成功，请开始使用GPU\n任务ID: {request_id}"
    return "❌ 确认失败，请求已超时或不存在"

def complete_gpu_request(request_id: int):
    """完成GPU使用"""
    gpu_manager.complete_request(request_id)
    return f"✅ 任务完成，GPU已释放\n任务ID: {request_id}"
