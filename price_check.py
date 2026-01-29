from playwright.sync_api import sync_playwright
import os

URL = "https://search.shopping.naver.com/catalog/53549966161"

BOT_TOKEN = os.environ["BOT_TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]

def send(msg):
    import requests
    requests.get(
        f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
        params={"chat_id": CHAT_ID, "text": msg}
    )

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    )
    page.goto(URL, timeout=60000)
    page.wait_for_timeout(5000)

    # 👉 화면에 보이는 '최저가' 텍스트
    price_text = page.locator("strong.price_real").first.inner_text()
    browser.close()

price = int(price_text.replace(",", "").replace("원", ""))

if os.path.exists("last_price.txt"):
    last = int(open("last_price.txt").read())
else:
    send(f"📌 가격 추적 시작\n현재 최저가: {price:,}원")
    open("last_price.txt", "w").write(str(price))
    exit()

if price != last:
    send(
        f"📉 네이버 쇼핑 최저가 변동!\n"
        f"이전: {last:,}원\n"
        f"현재: {price:,}원"
    )
    open("last_price.txt", "w").write(str(price))
