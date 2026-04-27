import requests

from services.config import settings


def send_telegram_alert(message: str) -> None:
    if not settings.TELEGRAM_BOT_TOKEN or not settings.TELEGRAM_CHAT_ID:
        return

    url = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": settings.TELEGRAM_CHAT_ID, "text": message, "disable_web_page_preview": True}
    try:
        requests.post(url, json=payload, timeout=10)
    except requests.RequestException:
        pass
