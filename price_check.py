from playwright.sync_api import sync_playwright
import requests
import os
import re

# ====== 설정 ======
URL = "https://search.shopping.naver.com/catalog/53549966161"
BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]

PRICE_FILE = "last_price.txt"


def send_telegram(msg):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, data={
        "chat_id": CHAT_ID,
        "text": msg
    })


with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()

    page.goto(URL, timeout=60000)
    page.wait_for_timeout(5000)  # 렌더링 대기

    text = page.inner_text("body")

    browser.close()

# ====== 가격 추출 (숫자 + 원) ======
prices = re.findall(r"(\d{1,3}(?:,\d{3})+)원", text)

if not prices:
    send_telegram("❌ 가격을 찾지 못했습니다")
    raise Exception("Price not found")

# 가장 낮은 가격 선택
current_price = min(int(p.replace(",", "")) for p in prices)

# ====== 이전 가격과 비교 ======
if os.path.exists(PRICE_F_
