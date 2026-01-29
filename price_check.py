import os
import hashlib
import requests
from playwright.sync_api import sync_playwright

URL = "https://search.shopping.naver.com/catalog/53549966161?deliveryCharge=true"
STATE_FILE = "last_state.txt"

BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]


def send_telegram(msg):
    requests.post(
        f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
        data={"chat_id": CHAT_ID, "text": msg},
        timeout=10
    )


def get_page_state() -> str:
    """
    최저가 영역 DOM 전체를 문자열로 가져와
    해시값으로 변환
    """
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(URL, wait_until="networkidle", timeout=30000)

        # 네이버 쇼핑 가격 영역 전체
        body_html = page.locator("body").inner_html()

        browser.close()

    return hashlib.sha256(body_html.encode("utf-8")).hexdigest()


def read_last_state():
    if not os.path.exists(STATE_FILE):
        return None
    return open(STATE_FILE).read().strip()


def save_state(state):
    with open(STATE_FILE, "w") as f:
        f.write(state)


def main():
    try:
        current_state = get_page_state()
    except Exception as e:
        send_telegram(f"❌ 페이지 상태 확인 실패\n에러: {e}")
        raise

    last_state = read_last_state()

    if last_state is None:
        save_state(current_state)
        send_telegram("📌 최초 상태 저장 완료 (이후 변동 시 알림)")
        return

    if current_state != last_state:
        send_telegram(
            "📉 가격 또는 상품 상태 변동 감지!\n\n"
            "배송비포함 최저가 영역에 변화가 있습니다.\n\n"
            f"{URL}"
        )
        save_state(current_state)
    else:
        print("변동 없음")


if __name__ == "__main__":
    main()
