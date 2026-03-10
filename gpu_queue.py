import sqlite3
import time
from datetime import datetime
from enum import Enum
from typing import List, Optional
import threading

class RequestStatus(Enum):
    PENDING = "pending"
    NOTIFIED = "notified"  # 已通知，等待确认
    CONFIRMED = "confirmed"  # 用户已确认使用
    COMPLETED = "completed"
    TIMEOUT = "timeout"  # 超时未确认
    CANCELLED = "cancelled"

class GPUQueueManager:
    def __init__(self, db_path="gpu_queue.db", max_concurrent=4):
        self.db_path = db_path
        self.max_concurrent = max_concurrent
        self.lock = threading.Lock()
        self._init_db()

    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS gpu_requests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                user_name TEXT,
                gpu_count INTEGER DEFAULT 1,
                priority INTEGER DEFAULT 0,
                status TEXT DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                notified_at TIMESTAMP,
                confirmed_at TIMESTAMP,
                completed_at TIMESTAMP,
                description TEXT
            )
        """)
        conn.commit()
        conn.close()

    def add_request(self, user_id: str, user_name: str = "", gpu_count: int = 1, priority: int = 0, description: str = "") -> int:
        """添加GPU请求到队列"""
        with self.lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.execute(
                "INSERT INTO gpu_requests (user_id, user_name, gpu_count, priority, description) VALUES (?, ?, ?, ?, ?)",
                (user_id, user_name, gpu_count, priority, description)
            )
            request_id = cursor.lastrowid
            conn.commit()
            conn.close()
            return request_id

    def get_queue_position(self, request_id: int) -> Optional[int]:
        """获取请求在队列中的位置"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.execute(
            "SELECT COUNT(*) FROM gpu_requests WHERE status='pending' AND (priority > (SELECT priority FROM gpu_requests WHERE id=?) OR (priority = (SELECT priority FROM gpu_requests WHERE id=?) AND id < ?))",
            (request_id, request_id, request_id)
        )
        position = cursor.fetchone()[0] + 1
        conn.close()
        return position

    def check_and_notify(self) -> List[dict]:
        """检查是否有空闲资源，通知排队用户"""
        with self.lock:
            conn = sqlite3.connect(self.db_path)

            # 检查已确认使用的数量
            cursor = conn.execute("SELECT COUNT(*) FROM gpu_requests WHERE status='confirmed'")
            confirmed_count = cursor.fetchone()[0]

            if confirmed_count >= self.max_concurrent:
                conn.close()
                return []

            # 检查超时的通知（5分钟）
            cursor = conn.execute(
                "SELECT id FROM gpu_requests WHERE status='notified' AND notified_at < datetime('now', '-5 minutes')"
            )
            timeout_ids = [row[0] for row in cursor.fetchall()]
            if timeout_ids:
                conn.execute(f"UPDATE gpu_requests SET status='timeout' WHERE id IN ({','.join('?'*len(timeout_ids))})", timeout_ids)

            # 获取可通知的数量
            available_slots = self.max_concurrent - confirmed_count
            cursor = conn.execute(
                "SELECT id, user_id, user_name, gpu_count FROM gpu_requests WHERE status='pending' ORDER BY priority DESC, created_at ASC LIMIT ?",
                (available_slots,)
            )
            requests = cursor.fetchall()

            notified = []
            for req in requests:
                conn.execute(
                    "UPDATE gpu_requests SET status='notified', notified_at=? WHERE id=?",
                    (datetime.now(), req[0])
                )
                notified.append({"id": req[0], "user_id": req[1], "user_name": req[2], "gpu_count": req[3]})

            conn.commit()
            conn.close()
            return notified

    def confirm_request(self, request_id: int) -> bool:
        """用户确认使用GPU"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.execute("SELECT status FROM gpu_requests WHERE id=?", (request_id,))
        row = cursor.fetchone()
        if row and row[0] == 'notified':
            conn.execute("UPDATE gpu_requests SET status='confirmed', confirmed_at=? WHERE id=?", (datetime.now(), request_id))
            conn.commit()
            conn.close()
            return True
        conn.close()
        return False

    def complete_request(self, request_id: int):
        """标记请求完成"""
        conn = sqlite3.connect(self.db_path)
        conn.execute(
            "UPDATE gpu_requests SET status='completed', completed_at=? WHERE id=?",
            (datetime.now(), request_id)
        )
        conn.commit()
        conn.close()

    def get_queue_status(self) -> dict:
        """获取队列状态"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.execute("SELECT status, COUNT(*) FROM gpu_requests WHERE status IN ('pending', 'notified', 'confirmed') GROUP BY status")
        status = dict(cursor.fetchall())
        conn.close()
        return {
            "pending": status.get("pending", 0),
            "notified": status.get("notified", 0),
            "confirmed": status.get("confirmed", 0),
            "available_slots": self.max_concurrent - status.get("confirmed", 0)
        }
