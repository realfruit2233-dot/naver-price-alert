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
m = re.search(r'"lowPrice":(\d+)', html)

if not m:
    print("가격 못 찾음")
    exit()

price = int(m.group(1))

if os.path.exists("last_price.txt"):
    last = int(open("last_price.txt").read())
else:
    last = price

if price != last:
    send(f"📉 네이버 쇼핑 최저가 변동\n이전: {last:,}원\n현재: {price:,}원")
    open("last_price.txt","w").write(str(price))
