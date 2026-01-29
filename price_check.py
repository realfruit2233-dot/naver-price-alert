import requests
import os

CATALOG_ID = "53549966161"
API_URL = f"https://search.shopping.naver.com/api/products/{CATALOG_ID}"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Referer": "https://search.shopping.naver.com/",
    "Accept": "application/json"
}

BOT_TOKEN = os.environ["BOT_TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]

def send(msg):
    requests.get(
        f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
        params={"chat_id": CHAT_ID, "text": msg}
    )

res = requests.get(API_URL, headers=HEADERS, timeout=10)

# 👉 여기서 차단 여부 먼저 체크
if res.status_code != 200:
    send(f"❌ 네이버 API 접근 실패 (status {res.status_code})")
    exit()

try:
    data = res.json()
except Exception:
    send("❌ JSON 파싱 실패 (네이버 차단/구조 변경)")
    exit()

# 👉 실제 최저가 위치
price = data["price"]["lowestPrice"]

# 이전 가격 비교
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
