import os
import re
import requests
from playwright.sync_api import sync_playwright

# ===== 설정 =====
URL = "https://search.shopping.naver.com/catalog/53549966161?deliveryCharge=true&cardDiscount=false&isNPayPlus=false&isUnitPriceOrder=false&purchaseConditionSequence="
PRICE_FILE = "last_price.txt"

BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]


def send_telegram(message: str):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": message}, timeout=10)


def extract_delivery_lowest_price(text: str) -> int:
    """
    네이버 쇼핑 '배송비포함 최저가' 모든 변형 패턴 대응
    """
    patterns = [
        r"배송비\s*포함\s*최저\s*([\d,]+)\s*원",
        r"배송비\s*포함[\s\S]{0,20}?([\d,]+)\s*원",
        r"최저\s*([\d,]+)\s*원[\s\S]{0,20}?배송비\s*포함",
        r"최저가\s*([\d,]+)\s*원",
    ]

    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            return int(match.group(1).replace(",", ""))

    raise ValueError("배송비포함 최저가 패턴 매칭 실패")


def get_current_price() -> int:
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            )
        )

        page.goto(URL, wait_until="networkidle", timeout=30000)

        # 페이지 전체 텍스트 확보 (React 렌더링 대응)
        body_text = page.locator("body").inner_text(timeout=30000)

        browser.close()
        return extract_delivery_lowest_price(body_text)


def read_last_price():
    if not os.path.exists(PRICE_FILE):
        return None
    with open(PRICE_FILE, "r", encoding="utf-8") as f:
        return int(f.read().strip())


def save_price(price: int):
    with open(PRICE_FILE, "w", encoding="utf-8") as f:
        f.write(str(price))


def main():
    try:
        current_price = get_current_price()
    except Exception as e:
        send_telegram(f"❌ 배송비포함 최저가 추출 실패\n에러: {e}")
        raise

    last_price = read_last_price()

    if last_price is None:
        save_price(current_price)
        send_telegram(f"📌 배송비포함 최저가 최초 저장: {current_price:,}원")
        return

    if current_price != last_price:
        send_telegram(
            "📉 배송비포함 최저가 변동!\n\n"
            f"이전 가격: {last_price:,}원\n"
            f"현재 가격: {current_price:,}원\n\n"
            f"{URL}"
        )
        save_price(current_price)
    else:
        print("가격 변동 없음")


if __name__ == "__main__":
    main()
