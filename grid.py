import ccxt
import time
import requests
import os
from flask import Flask
from threading import Thread

app = Flask(__name__)

# Env'ler
API_KEY = os.environ.get('mBblexRrtF9bglEA5X6ynSDNZLtciK3VV09fRGVFYGbR2irm9aQSd1wRnH8pqFpq')
API_SECRET = os.environ.get('Bp7YyGrNnR1KMZTMpfGNg9TFqDd27Ivgk8HUCuBtBLp8S2OtGr9AoqWnlUoqmbiq')
TELEGRAM_TOKEN = os.environ.get('8498989500:AAGmk-2OBpal04K4i6ZMk6YaYNC79Fa_xac')
TELEGRAM_CHAT_ID = os.environ.get('8120732989')
SYMBOL = 'SOLUSDT'
AMOUNT = float(os.environ.get('AMOUNT', 10))
LEVERAGE = int(os.environ.get('LEVERAGE', 3))
GRID_COUNT = 8
GRID_INTERVAL_PCT = 0.006  # %0.6

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
        requests.post(url, data=data, timeout=10)
    except:
        pass

def set_leverage():
    try:
        exchange.fapiPrivate_post_leverage({'symbol': SYMBOL, 'leverage': LEVERAGE})
        exchange.fapiPrivate_post_marginType({'symbol': SYMBOL, 'marginType': 'ISOLATED'})
        send_telegram(f"☁️ Grid Bot Aktif - {SYMBOL} {LEVERAGE}x İzole")
    except Exception as e:
        send_telegram(f"Leverage hata: {str(e)}")

def create_grid():
    try:
        price = float(exchange.fetch_ticker(SYMBOL)['last'])
        interval = price * GRID_INTERVAL_PCT
        qty = AMOUNT / (price * LEVERAGE * GRID_COUNT)

        send_telegram(f"🛠️ Grid kuruluyor - Başlangıç: {price:.2f}")

        for i in range(GRID_COUNT):
            buy_price = price - (i + 1) * interval
            sell_price = price + (i + 1) * interval
            exchange.create_limit_buy_order(SYMBOL, qty, buy_price)
            exchange.create_limit_sell_order(SYMBOL, qty, sell_price)

        send_telegram("✅ Grid kuruldu!")
    except Exception as e:
        send_telegram(f"Grid hata: {str(e)}")

def monitor():
    while True:
        try:
            price = float(exchange.fetch_ticker(SYMBOL)['last'])
            positions = exchange.fapiPrivate_get_positionrisk({'symbol': SYMBOL})
            for pos in positions:
                pnl = float(pos['unrealizedProfit'])
                if pnl > 0.2 * AMOUNT:
                    send_telegram(f"💰 Kar: +{pnl:.2f}$ - Kısmi al?")
            time.sleep(60)
        except:
            time.sleep(300)

@app.route('/')
def home():
    return "Grid Bot Çalışıyor"

if __name__ == "__main__":
    send_telegram("🚀 Grid Bot v3 Başladı - 10$ + 3x İzole + SOLUSDT")
    set_leverage()
    create_grid()
    Thread(target=monitor, daemon=True).start()
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))
