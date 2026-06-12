import requests
import os

BOT_TOKEN = os.environ["BOT_TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]
API_KEY = os.environ["BIZINFO_API_KEY"]

URL = "https://www.bizinfo.go.kr/uss/rss/bizinfoApi.do"


def send_telegram(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, data={
        "chat_id": CHAT_ID,
        "text": message,
        "disable_web_page_preview": True
    })


def main():
    # JSON으로 시도
    params = {
        "crtfcKey": API_KEY,
        "dataType": "json",
        "searchCnt": "3",
    }
    try:
        res = requests.get(URL, params=params, timeout=30)
        print(f"상태: {res.status_code}")
        print(f"응답: {res.text[:2000]}")
        send_telegram(f"🔍 기업마당 API 응답\n상태: {res.status_code}\n\n{res.text[:1200]}")
    except Exception as e:
        send_telegram(f"❌ 오류: {str(e)[:300]}")


if __name__ == "__main__":
    main()
