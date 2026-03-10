import requests
import config
import json

def get_tenant_access_token():
    url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
    data = {
        "app_id": config.FEISHU_APP_ID,
        "app_secret": config.FEISHU_APP_SECRET
    }
    response = requests.post(url, json=data)
    return response.json().get("tenant_access_token")

def get_user_name(open_id):
    token = get_tenant_access_token()
    url = f"https://open.feishu.cn/open-apis/contact/v3/users/{open_id}"
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(url, headers=headers)
    result = response.json()
    print(f"用户信息完整响应: {json.dumps(result, indent=2, ensure_ascii=False)}")
    if result.get("data") and result["data"].get("user"):
        return result["data"]["user"].get("name", open_id)
    return open_id

def send_message(message_id, content):
    token = get_tenant_access_token()
    url = "https://open.feishu.cn/open-apis/im/v1/messages"
    headers = {"Authorization": f"Bearer {token}"}
    data = {
        "receive_id": message_id,
        "msg_type": "text",
        "content": json.dumps({"text": content})
    }
    response = requests.post(url, headers=headers, json=data, params={"receive_id_type": "open_id"})
    print(f"发送消息响应: {response.status_code}, {response.text}")
    return response.json()
