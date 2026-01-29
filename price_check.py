import requests
import os

CATALOG_ID = "53549966161"
API_URL = f"https://search.shopping.naver.com/api/catalogs/{CATALOG_ID}"

HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Referer": "https://search.shopping.naver.com/"
}

BOT_TOKEN = os.environ["BOT_TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]

def send(msg):
    requests.get(
        f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
        params={"chat_id": CHAT_ID, "text": msg}
    )

res = requests.get(API_URL, headers=HEADERS)
data = res.json()

# 최저가 추출 (네이버 공식 필드)
price = data["price"]["lowPrice"]

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
