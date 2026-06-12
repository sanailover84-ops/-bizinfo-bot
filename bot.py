import requests
import os
import time

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
    report = "🔬 진단 시작\n\n"

    # 1단계: 키 앞 4자리 확인 (전체 노출 안 함)
    report += f"1) API_KEY 길이: {len(API_KEY)}자, 앞2자: {API_KEY[:2]}\n\n"

    # 2단계: API 호출 (시간 측정)
    params = {
        "crtfcKey": API_KEY,
        "dataType": "json",
        "searchCnt": "10",
    }
    start = time.time()
    try:
        res = requests.get(URL, params=params, timeout=25)
        elapsed = round(time.time() - start, 1)
        report += f"2) 호출 성공! 소요 {elapsed}초, 상태코드 {res.status_code}\n\n"

        # 3단계: 응답 내용 앞부분
        report += f"3) 응답 앞 300자:\n{res.text[:300]}\n\n"

        # 4단계: JSON 파싱 시도
        try:
            data = res.json()
            keys = list(data.keys())
            report += f"4) JSON 키: {keys}\n"
            arr = data.get("jsonArray", "키없음")
            if isinstance(arr, list):
                report += f"   jsonArray 건수: {len(arr)}\n"
            else:
                report += f"   jsonArray: {arr}\n"
        except Exception as je:
            report += f"4) JSON 파싱 실패: {str(je)[:100]}\n"

    except Exception as e:
        elapsed = round(time.time() - start, 1)
        report += f"2) 호출 실패! 소요 {elapsed}초\n오류: {str(e)[:200]}\n"

    send_telegram(report)
    print(report)


if __name__ == "__main__":
    main()
