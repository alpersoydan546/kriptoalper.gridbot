import ccxt
import time
import requests
import os

# ================== ENV KONTROLLERİ ==================
API_KEY = os.environ.get('mBblexRrtF9bglEA5X6ynSDNZLtciK3VV09fRGVFYGbR2irm9aQSd1wRnH8pqFpq')
API_SECRET = os.environ.get('Bp7YyGrNnR1KMZTMpfGNg9TFqDd27Ivgk8HUCuBtBLp8S2OtGr9AoqWnlUoqmbiq')
TELEGRAM_TOKEN = os.environ.get('8498989500:AAGmk-2OBpal04K4i6ZMk6YaYNC79Fa_xac')
TELEGRAM_CHAT_ID = os.environ.get('8120732989')
SYMBOL = 'SOLUSDT'
AMOUNT = float(os.environ.get('AMOUNT', 10))
LEVERAGE = int(os.environ.get('LEVERAGE', 3))

# Env kontrolü
if not all([API_KEY, API_SECRET, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID]):
    print("❌ EKSİK ENV VARIABLE! Lütfen Render'da şu 4 tanesini ekle:")
    print("API_KEY, API_SECRET, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID")
    exit()

exchange = ccxt.binance({
    'apiKey': API_KEY,
    'secret': API_SECRET,
    'enableRateLimit': True,
    'options': {'defaultType': 'future'}
})

def send_telegram(message):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        data = {"chat_id": TELEGRAM_CHAT_ID, "text": message, "parse_mode": "HTML"}
        r = requests.post(url, data=data, timeout=10)
        if r.status_code != 200:
            print(f"Telegram hatası: {r.text}")
    except Exception as e:
        print(f"Telegram gönderme hatası: {e}")

print("✅ Grid Bot başlatılıyor...")

def set_leverage():
    try:
        exchange.fapiPrivate_post_leverage({'symbol': SYMBOL, 'leverage': LEVERAGE})
        exchange.fapiPrivate_post_marginType({'symbol': SYMBOL, 'marginType': 'ISOLATED'})
        send_telegram(f"☁️ Grid Bot Aktif\n{SYMBOL} - {LEVERAGE}x İzole\n10$ ile başlıyor")
        print("✅ Leverage ve İzole mod ayarlandı")
    except Exception as e:
        send_telegram(f"⚠️ Leverage hatası: {str(e)}")
        print(f"Leverage hatası: {e}")

def create_grid():
    try:
        price = float(exchange.fetch_ticker(SYMBOL)['last'])
        interval = price * 0.006   # %0.6 aralık
        qty = AMOUNT / (price * LEVERAGE * 8)

        send_telegram(f"🛠️ Grid kuruluyor...\nBaşlangıç fiyat: {price:.2f}\n8 grid × %0.6 aralık")

        for i in range(8):
            buy_price = price - (i + 1) * interval
            sell_price = price + (i + 1) * interval
            exchange.create_limit_buy_order(SYMBOL, qty, buy_price)
            exchange.create_limit_sell_order(SYMBOL, qty, sell_price)

        send_telegram("✅ Grid başarıyla kuruldu! Artık otomatik işlem yapıyor.")
        print("✅ Grid kuruldu")
    except Exception as e:
        send_telegram(f"❌ Grid kurulum hatası: {str(e)}")
        print(f"Grid hatası: {e}")

# ===================== ANA ÇALIŞMA =====================
if __name__ == "__main__":
    send_telegram("🚀 Grid Bot v2 Başladı - 10$ + 3x İzole + SOLUSDT")
    set_leverage()
    create_grid()
    
    # Basit monitor (sadece aralık kontrolü)
    while True:
        time.sleep(300)  # 5 dakikada bir kontrol
