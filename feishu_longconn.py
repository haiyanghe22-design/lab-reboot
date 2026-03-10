import lark_oapi as lark
import config
from agent import chat
from skills.feishu_client import send_message, get_user_name
from scheduler import start_scheduler
import json
import os
from datetime import datetime

SESSIONS_DIR = "sessions"

def get_user_session_dir(user_id):
    user_dir = os.path.join(SESSIONS_DIR, user_id)
    os.makedirs(user_dir, exist_ok=True)
    return user_dir

def load_processed_messages(user_id):
    processed_file = os.path.join(get_user_session_dir(user_id), "processed.txt")
    if os.path.exists(processed_file):
        with open(processed_file, 'r') as f:
            return set(line.strip() for line in f)
    return set()

def save_processed_message(user_id, message_id):
    processed_file = os.path.join(get_user_session_dir(user_id), "processed.txt")
    with open(processed_file, 'a') as f:
        f.write(f"{message_id}\n")

def save_conversation(user_id, user_msg, bot_response):
    session_file = os.path.join(get_user_session_dir(user_id), f"{datetime.now().strftime('%Y%m%d')}.txt")
    with open(session_file, 'a', encoding='utf-8') as f:
        f.write(f"[{datetime.now().strftime('%H:%M:%S')}] 用户: {user_msg}\n")
        f.write(f"[{datetime.now().strftime('%H:%M:%S')}] 机器人: {bot_response}\n\n")

user_processed_messages = {}

def do_p2_im_message_receive_v1(data: lark.im.v1.P2ImMessageReceiveV1) -> None:
    try:
        message = data.event.message
        message_id = message.message_id
        sender_id = data.event.sender.sender_id.open_id

        if sender_id not in user_processed_messages:
            user_processed_messages[sender_id] = load_processed_messages(sender_id)

        if message_id in user_processed_messages[sender_id]:
            print(f"消息 {message_id} 已处理过，跳过")
            return

        user_processed_messages[sender_id].add(message_id)
        save_processed_message(sender_id, message_id)

        content_str = message.content
        content = json.loads(content_str)
        text = content.get("text", "")
        sender_name = get_user_name(sender_id)

        print(f"消息内容: {text}, 发送者: {sender_name}")

        response = chat(text, user_id=sender_id, user_name=sender_name)
        send_message(sender_id, response)
        save_conversation(sender_id, text, response)

    except Exception as e:
        print(f"处理消息出错: {e}")
        import traceback
        traceback.print_exc()

event_handler = lark.EventDispatcherHandler.builder("", "") \
    .register_p2_im_message_receive_v1(do_p2_im_message_receive_v1) \
    .build()

def main():
    cli = lark.ws.Client(config.FEISHU_APP_ID, config.FEISHU_APP_SECRET,
                         event_handler=event_handler,
                         log_level=lark.LogLevel.DEBUG)
    cli.start()

if __name__ == "__main__":
    print("启动飞书长连接...")
    start_scheduler()
    main()
