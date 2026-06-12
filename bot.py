import requests
import os
from datetime import datetime

BOT_TOKEN = os.environ["BOT_TOKEN"]
CHAT_IDS = [
    os.environ["CHAT_ID"],
    os.environ.get("CHAT_ID_2", ""),
]
CHAT_IDS = [c for c in CHAT_IDS if c]
API_KEY = os.environ["BIZINFO_API_KEY"]

URL = "https://www.bizinfo.go.kr/uss/rss/bizinfoApi.do"

# ✅ 관심 키워드
KEYWORDS = ["융자", "보증", "기금", "특허", "바우처"]

# ✅ 웹페이지 주소 (GitHub Pages)
WEB_URL = "https://sanailover84-ops.github.io/bizinfo-bot/"


def send_telegram(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    max_len = 4000
    chunks = [message[i:i+max_len] for i in range(0, len(message), max_len)]
    for chat_id in CHAT_IDS:
        for chunk in chunks:
            requests.post(url, data={
                "chat_id": chat_id,
                "text": chunk,
                "parse_mode": "Markdown",
                "disable_web_page_preview": True
            })


def get_bizinfo():
    """기업마당 지원사업 전체 조회"""
    items = []
    try:
        params = {
            "crtfcKey": API_KEY,
            "dataType": "json",
            "searchCnt": "500",
        }
        res = requests.get(URL, params=params, timeout=30)
        data = res.json()
        # 응답 구조: jsonArray 안에 목록
        items = data.get("jsonArray", [])
    except Exception as e:
        print(f"API 오류: {e}")
        # 디버그용: 응답 원본 일부 전송
        try:
            send_telegram(f"⚠️ API 디버그\n{res.text[:500]}")
        except Exception:
            pass
    return items


def parse_item(item):
    def g(key):
        return str(item.get(key, "")).strip()
    return {
        "title": g("pblancNm"),          # 공고명
        "summary": g("bsnsSumryCn"),     # 사업요약
        "period": g("reqstBeginEndDe"),  # 신청기간
        "dept": g("jrsdInsttNm"),        # 소관기관
        "exec": g("excInsttNm"),         # 수행기관
        "url": g("pblancUrl"),           # 상세링크
        "hashtags": g("hashtags"),       # 해시태그
        "field": g("pldirSportRealmLclasCodeNm"),  # 지원분야
        "target": g("trgetNm"),          # 대상
        "regdate": g("creatPnttm"),      # 등록일
    }


def clean(text, n=100):
    text = " ".join(text.split())
    return text[:n] + "..." if len(text) > n else text


def main():
    today = datetime.now().strftime("%Y년 %m월 %d일 (%A)")
    day_map = {
        "Monday": "월요일", "Tuesday": "화요일", "Wednesday": "수요일",
        "Thursday": "목요일", "Friday": "금요일", "Saturday": "토요일", "Sunday": "일요일"
    }
    for en, ko in day_map.items():
        today = today.replace(en, ko)

    raw_items = get_bizinfo()
    all_data = [parse_item(it) for it in raw_items]

    # 키워드 매칭 (공고명 + 요약 + 해시태그에서 검색)
    matched = []
    for d in all_data:
        search_text = f"{d['title']} {d['summary']} {d['hashtags']}"
        hit_kw = [kw for kw in KEYWORDS if kw in search_text]
        if hit_kw:
            d["matched_kw"] = hit_kw
            matched.append(d)

    msg = f"💼 *{today} 기업지원사업 브리핑*\n"
    msg += "━━━━━━━━━━━━━━━━━━━━\n\n"

    if matched:
        msg += f"🔔 *키워드 매칭 지원사업 ({len(matched)}건)*\n"
        msg += f"_(융자·보증·기금·특허·바우처)_\n\n"
        for d in matched[:12]:
            kw_tag = "·".join(d["matched_kw"])
            msg += f"• *{d['title']}*\n"
            msg += f"  🏷 {kw_tag}\n"
            if d['dept']:
                msg += f"  🏛 {d['dept']}\n"
            if d['period']:
                msg += f"  📅 {d['period']}\n"
            if d['url']:
                # 상대경로면 절대경로로
                link = d['url'] if d['url'].startswith("http") else f"https://www.bizinfo.go.kr{d['url']}"
                msg += f"  🔗 {link}\n"
            msg += "\n"
        if len(matched) > 12:
            msg += f"...외 {len(matched)-12}건 (웹페이지 참고)\n\n"
    else:
        msg += "오늘은 키워드 매칭 지원사업이 없습니다.\n\n"

    msg += "━━━━━━━━━━━━━━━━━━━━\n"
    msg += f"📊 전체 {len(all_data)}건 중 {len(matched)}건 매칭\n\n"
    msg += f"📋 *전체 목록 보기*\n{WEB_URL}"

    send_telegram(msg)
    generate_html(matched, all_data)
    print(f"✅ 전송 완료 - 전체 {len(all_data)}, 매칭 {len(matched)}")


def generate_html(matched, all_data):
    update_time = datetime.now().strftime("%Y-%m-%d %H:%M")

    html = f"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>기업지원사업 모아보기</title>
<style>
  * {{ box-sizing:border-box; }}
  body {{ font-family:-apple-system,'Malgun Gothic',sans-serif; background:#f5f6fa; margin:0; padding:16px; color:#2c3e50; }}
  h1 {{ text-align:center; font-size:23px; }}
  .update {{ text-align:center; color:#888; font-size:13px; margin-bottom:8px; }}
  .summary {{ text-align:center; margin-bottom:20px; }}
  .summary span {{ display:inline-block; background:#fff; padding:6px 14px; border-radius:20px; margin:4px; font-size:13px; box-shadow:0 1px 3px rgba(0,0,0,0.1); }}
  .section-title {{ font-size:18px; font-weight:bold; margin:20px 0 12px; padding-bottom:8px; border-bottom:2px solid #e74c3c; }}
  .item {{ background:#fff; border-radius:10px; padding:14px; margin-bottom:12px; box-shadow:0 1px 4px rgba(0,0,0,0.06); }}
  .item-title {{ font-weight:bold; font-size:15px; margin-bottom:6px; }}
  .kw {{ display:inline-block; background:#e74c3c; color:#fff; font-size:11px; padding:2px 8px; border-radius:10px; margin-right:4px; }}
  .meta {{ color:#666; font-size:13px; margin:3px 0; }}
  .link {{ display:inline-block; margin-top:8px; background:#3498db; color:#fff; padding:6px 14px; border-radius:6px; font-size:13px; text-decoration:none; }}
</style>
</head>
<body>
<h1>💼 기업지원사업 모아보기</h1>
<div class="update">마지막 업데이트: {update_time}</div>
<div class="summary">
  <span>📊 전체 {len(all_data)}건</span>
  <span>🔔 키워드 매칭 {len(matched)}건</span>
</div>
<div class="section-title">🔔 키워드 매칭 (융자·보증·기금·특허·바우처)</div>
"""

    for d in matched:
        html += '<div class="item">\n'
        html += f'<div class="item-title">{d["title"]}</div>\n'
        for kw in d["matched_kw"]:
            html += f'<span class="kw">{kw}</span>'
        html += '<div style="margin-top:6px;"></div>'
        if d['dept']:
            html += f'<div class="meta">🏛 {d["dept"]}</div>\n'
        if d['period']:
            html += f'<div class="meta">📅 {d["period"]}</div>\n'
        if d['summary']:
            html += f'<div class="meta">📝 {clean(d["summary"], 150)}</div>\n'
        if d['url']:
            link = d['url'] if d['url'].startswith("http") else f"https://www.bizinfo.go.kr{d['url']}"
            html += f'<a class="link" href="{link}" target="_blank">자세히 보기 →</a>\n'
        html += '</div>\n'

    html += "</body></html>"

    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html)
    print("✅ index.html 생성 완료")


if __name__ == "__main__":
    main()
