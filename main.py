import requests
import time
import uuid
import json
import os
from dotenv import load_dotenv

load_dotenv()

PANEL_URL = os.getenv("PANEL_URL")
SUB_URL = os.getenv("SUB_URL")
USERNAME = os.getenv("USERNAME")
PASSWORD = os.getenv("PASSWORD")
INBOUND_ID = os.getenv("INBOUND_ID")

session = requests.Session()

def login():
    url = f"{PANEL_URL}/login"
    data = {"username": USERNAME, "password": PASSWORD}
    resp = session.post(url, json=data)
    if resp.status_code == 200 and session.cookies.get("3x-ui"):
        print("✅ Авторизация прошла успешно!")
        return True
    print("❌ Ошибка при авторизации.")
    return False

def get_subscription_link(username):
    return f"https://guardport.ru:2096/c3Vic2NpcHRpb24=/{username}"

def add_client(username):
    url = f"{PANEL_URL}/panel/api/inbounds/addClient"
    expiry_timestamp = int(time.time()) + 30 * 86400
    user_uuid = str(uuid.uuid4())

    client = {
        "id": user_uuid,
        "email": username,
        "limitIp": 0,
        "totalGB": 0,
        "expiryTime": expiry_timestamp * 1000,
        "enable": True,
        "tgId": "",
        "subId": username,
        "reset": 0
    }

    payload = {
        "id": INBOUND_ID,
        "settings": json.dumps({"clients": [client]})  # Строка с JSON
    }

    headers = {
        "Content-Type": "application/json"
    }

    print("[DEBUG] Payload:", json.dumps(payload, indent=2))

    resp = session.post(url, json=payload, headers=headers)
    link = get_subscription_link(username)
    if resp.status_code == 200:
        print("✅ Клиент успешно добавлен!")
        print("UUID:", user_uuid)
        print("Истекает:", time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(expiry_timestamp)))
        print("Ответ сервера:", resp.json())
        print("Ссылка на подписку:", link)
    else:
        print("❌ Ошибка при добавлении клиента:", resp.status_code, resp.text)

if __name__ == "__main__":
    username = input("Введите имя пользователя: ").strip()
    if login():
        add_client(username)