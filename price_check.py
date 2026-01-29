import requests
import re
import os

URL = "https://search.shopping.naver.com/catalog/53549966161"
HEADERS = {"User-Agent": "Mozilla/5.0"}

BOT_TOKEN = os.environ["BOT_TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]

def send(msg):
    requests.get(
        f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
        params={"chat_id": CHAT_ID, "text": msg}
    )

html = requests.get(URL, headers=HEADERS).text

patterns = [
    r'"lowPrice":\s*(\d+)',
    r'"lowestPrice":\s*(\d+)',
    r'"price":\s*(\d+)'
]

price = None
for p in patterns:
    m = re.search(p, html)
    if m:
        price = int(m.group(1))
        break

if price is None:
    send("❌ 가격 파싱 실패 (네이버 구조 변경 가능)")
    exit()

if os.path.exists("last_price.txt"):
    last = int(open("last_price.txt").read())
else:
    last = price

if price != last:
    send(f"📉 네이버 쇼핑 최저가 변동!\n이전: {last:,}원\n현재: {price:,}원")
    open("last_price.txt","w").write(str(price))
