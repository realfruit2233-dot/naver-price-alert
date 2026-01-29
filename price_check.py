import os
import re
import requests
from playwright.sync_api import sync_playwright

URL = "https://search.shopping.naver.com/catalog/53549966161?deliveryCharge=true"
PRICE_FILE = "last_price.txt"

BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]


def send_telegram(msg):
    requests.post(
        f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
        data={"chat_id": CHAT_ID, "text": msg},
        timeout=10
    )


def extract_lowest_price(page) -> int:
    """
    배송비포함 옵션이 켜진 상태에서
    '최저가 영역의 strong 가격' 직접 추출
    """

    # 네이버 쇼핑 최저가 영역은 strong 태그에 원화 표시
    price_nodes = page.locator("strong")

    count = price_nodes.count()
    prices = []

    for i in range(count):
        text = price_nodes.nth(i).inner_text().strip()
        if "원" in text:
            m = re.search(r"(\d{1,3}(?:,\d{3})+)\s*원", text)
            if m:
                prices.append(int(m.group(1).replace(",", "")))

    if not prices:
        raise ValueError("가격 strong 태그 추출 실패")

    return min(prices)


def get_current_price():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(URL, wait_until="networkidle", timeout=30000)

        price = extract_lowest_price(page)

        browser.close()
        return price


def read_last_price():
    if not os.path.exists(PRICE_FILE):
        return None
    return int(open(PRICE_FILE).read().strip())


def save_price(price):
    with open(PRICE_FILE, "w") as f:
        f.write(str(price))


def main():
    try:
        current_price = get_current_price()
    except Exception as e:
        send_telegram(f"❌ 가격 추출 실패\n에러: {e}")
        raise

    last_price = read_last_price()

    if last_price is None:
        save_price(current_price)
        send_telegram(f"📌 최초 저장 가격: {current_price:,}원")
        return

    if current_price != last_price:
        send_telegram(
            "📉 가격 변동 감지!\n\n"
            f"이전: {last_price:,}원\n"
            f"현재: {current_price:,}원\n\n"
            f"{URL}"
        )
        save_price(current_price)
    else:
        print("가격 변동 없음")


if __name__ == "__main__":
    main()
