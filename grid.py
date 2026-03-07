import ccxt
import time
import requests
import os

# Env'ler
API_KEY = os.environ.get('mBblexRrtF9bglEA5X6ynSDNZLtciK3VV09fRGVFYGbR2irm9aQSd1wRnH8pqFpq')
API_SECRET = os.environ.get('Bp7YyGrNnR1KMZTMpfGNg9TFqDd27Ivgk8HUCuBtBLp8S2OtGr9AoqWnlUoqmbiq')
TELEGRAM_TOKEN = os.environ.get('8498989500:AAGmk-2OBpal04K4i6ZMk6YaYNC79Fa_xac')
TELEGRAM_CHAT_ID = os.environ.get('8120732989')
SYMBOL = 'SOLUSDT'
AMOUNT = float(os.environ.get('AMOUNT', 10))
LEVERAGE = int(os.environ.get('LEVERAGE', 3))

if not all([API_KEY, API_SECRET, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID]):
    print("EKSİK ENV! API_KEY, API_SECRET, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID ekle.")
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
        print(f"Telegram yanıt: {r.status_code} - {r.text}")
    except Exception as e:
        print(f"Telegram hata: {e}")

print("Bot başlatılıyor...")

send_telegram("🚀 Grid Bot v4 BAŞLADI - 10$ + 3x izole + SOLUSDT")

def set_leverage():
    try:
        exchange.fapiPrivate_post_leverage({'symbol': SYMBOL, 'leverage': LEVERAGE})
        exchange.fapiPrivate_post_marginType({'symbol': SYMBOL, 'marginType': 'ISOLATED'})
        send_telegram("✅ 3x izole mod aktif")
        print("Leverage ayarlandı")
    except Exception as e:
        send_telegram(f"Leverage hata: {str(e)}")
        print(f"Leverage hata: {e}")

set_leverage()

# Test emir (küçük test için)
try:
    price = exchange.fetch_ticker(SYMBOL)['last']
    send_telegram(f"Şu an fiyat: {price:.2f}")
    print("Fiyat alındı")
except Exception as e:
    send_telegram(f"Fiyat alma hata: {str(e)}")
    print(f"Fiyat hata: {e}")

print("Bot çalışıyor - grid kurulumuna geçiliyor (test için yorum satırı)")
# create_grid() kısmını testten sonra aktif et
