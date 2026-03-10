import schedule
import time
import threading
import config
from skills.disk_usage.handler import get_disk_usage
from skills.feishu_client import send_message
from gpu_queue import GPUQueueManager

def check_disk():
    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] 开始检查磁盘...")
    try:
        disk_info = get_disk_usage()
        alerts = []

        for partition in disk_info['partitions']:
            if partition['used_percent'] >= config.DISK_THRESHOLD:
                alerts.append(f"{partition['mount_point']}: {partition['used_percent']}% ({partition['used_gb']}/{partition['total_gb']}GB)")

        if alerts:
            message = f"⚠️ 磁盘告警\n" + "\n".join(alerts)
        else:
            message = f"✅ 磁盘正常\n总计: {disk_info['overall_used_percent']}%"

        send_message(config.MONITOR_USER_ID, message)
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] 磁盘检查完成，消息已发送")
    except Exception as e:
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] 磁盘检查失败: {e}")

gpu_manager = GPUQueueManager(max_concurrent=4)

def allocate_gpu():
    """检查并通知有空闲GPU"""
    try:
        # 先获取超时的请求
        import sqlite3
        conn = sqlite3.connect(gpu_manager.db_path)
        cursor = conn.execute(
            "SELECT id, user_id, user_name FROM gpu_requests WHERE status='notified' AND notified_at < datetime('now', '-5 minutes')"
        )
        timeout_reqs = cursor.fetchall()
        conn.close()

        # 通知超时用户
        for req in timeout_reqs:
            message = f"⏰ GPU确认超时\n任务ID: {req[0]}\n已自动释放，请重新申请"
            send_message(req[1], message)
            print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] 用户 {req[2]} 超时未确认 (ID: {req[0]})")

        # 检查并通知下一位
        notified = gpu_manager.check_and_notify()
        for req in notified:
            message = f"🎮 GPU资源空闲\n任务ID: {req['id']}\n请在5分钟内回复确认使用\n回复格式: 确认 {req['id']}"
            send_message(req['user_id'], message)
            print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] 已通知用户 {req['user_name']} (ID: {req['id']})")
    except Exception as e:
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] GPU通知失败: {e}")

def start_scheduler():
    schedule.every().day.at(config.DISK_CHECK_TIME).do(check_disk)
    schedule.every(2).minutes.do(allocate_gpu)

    check_disk()
    allocate_gpu()

    def run():
        while True:
            schedule.run_pending()
            time.sleep(60)

    thread = threading.Thread(target=run, daemon=True)
    thread.start()
    print(f"定时任务已启动: 每日 {config.DISK_CHECK_TIME} 检查磁盘, 每2分钟分配GPU")
