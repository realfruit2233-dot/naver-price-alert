import os
import hashlib
import requests
from playwright.sync_api import sync_playwright

# ===== 설정 =====
URL = "https://search.shopping.naver.com/catalog/53549966161"
STATE_FILE = "page_state.txt"

BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]

# ===== 텔레그램 전송 =====
def send_telegram(message: str):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": message
    }
    requests.post(url, json=payload, timeout=10)

# ===== 페이지 핵심 내용 해시 =====
def get_page_hash():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        page.goto(URL, timeout=60000)
        page.wait_for_timeout(5000)  # JS 렌더링 대기

        # 네이버 쇼핑은 body 전체 텍스트가 제일 안정적
        body_text = page.locator("body").inner_text()

        browser.close()

    # 공백 정리 후 해시
    normalized = " ".join(body_text.split())
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()

# ===== 메인 로직 =====
def main():
    current_hash = get_page_hash()

    # 최초 실행 → 상태만 저장 (알림 ❌)
    if not os.path.exists(STATE_FILE):
        with open(STATE_FILE, "w") as f:
            f.write(current_hash)
        return

    with open(STATE_FILE, "r") as f:
        last_hash = f.read().strip()

    # 변동 감지
    if current_hash != last_hash:
        send_telegram(
            "🔔 네이버 쇼핑 페이지에 변동이 감지되었습니다!\n"
            "👉 최저가 / 구성 / 판매처 변경 가능성 있음\n\n"
            f"{URL}"
        )

        # 상태 업데이트
        with open(STATE_FILE, "w") as f:
            f.write(current_hash)

if __name__ == "__main__":
    main()
