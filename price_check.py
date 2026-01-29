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
    requests.post(
        url,
        data={"chat_id": CHAT_ID, "text": message},
        timeout=10
    )


def extract_price_from_dom(page) -> int:
    """
    화면에 보이는 '배송비포함' 문구 기준으로
    인접한 가격 DOM에서 숫자 추출
    """

    # '배송비포함' 이 들어간 모든 요소 찾기
    nodes = page.locator("text=/배송비\\s*포함/")

    count = nodes.count()
    if count == 0:
        raise ValueError("배송비포함 텍스트 노드 없음")

    for i in range(count):
        node = nodes.nth(i)

        # 부모 요소 기준으로 가격 텍스트 수집
        container = node.locator("xpath=ancestor::*[1]")
        text = container.inner_text()

        # 가격 패턴 찾기
        prices = re.findall(r"(\d{1,3}(?:,\d{3})+)\s*원", text)
        if prices:
            nums = [int(p.replace(",", "")) for p in prices]
            return min(nums)

    raise ValueError("배송비포함 인접 가격 추출 실패")


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

        price = extract_price_from_dom(page)

        browser.close()
        return price


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
