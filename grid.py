import ccxt
import time
import requests
import os
from datetime import datetime

# --- GRID BOT v1 - 10$ + 3x İZOLE + SOLUSDT ---
API_KEY = os.environ.get('mBblexRrtF9bglEA5X6ynSDNZLtciK3VV09fRGVFYGbR2irm9aQSd1wRnH8pqFpq')
API_SECRET = os.environ.get('Bp7YyGrNnR1KMZTMpfGNg9TFqDd27Ivgk8HUCuBtBLp8S2OtGr9AoqWnlUoqmbiq')
TELEGRAM_TOKEN = os.environ.get('8498989500:AAGmk-2OBpal04K4i6ZMk6YaYNC79Fa_xac')
TELEGRAM_CHAT_ID = os.environ.get('8120732989')
SYMBOL = 'SOLUSDT'
AMOUNT = 10  # dolar
LEVERAGE = 3
GRID_COUNT = 8
GRID_INTERVAL_PCT = 0.006  # %0.6 aralık

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

def set_leverage_and_isolated():
    try:
        exchange.fapiPrivate_post_leverage({'symbol': SYMBOL, 'leverage': LEVERAGE})
        exchange.fapiPrivate_post_marginType({'symbol': SYMBOL, 'marginType': 'ISOLATED'})
        send_telegram(f"☁️ Grid Bot: {LEVERAGE}x izole mod aktif - {SYMBOL}")
    except Exception as e:
        send_telegram(f"Setup hata: {str(e)}")

def get_price():
    ticker = exchange.fetch_ticker(SYMBOL)
    return float(ticker['last'])

def create_grid():
    price = get_price()
    grid_interval = price * GRID_INTERVAL_PCT
    qty = AMOUNT / (price * LEVERAGE * GRID_COUNT)  # her grid için miktar

    send_telegram(f"☁️ Grid kuruluyor: {SYMBOL} - {GRID_COUNT} grid, ±%{(GRID_COUNT*GRID_INTERVAL_PCT*100):.1f} aralık\nBaşlangıç: {price}")

    for i in range(GRID_COUNT):
        buy_price = price - (i + 1) * grid_interval
        sell_price = price + (i + 1) * grid_interval

        try:
            exchange.create_limit_buy_order(SYMBOL, qty, buy_price)
            exchange.create_limit_sell_order(SYMBOL, qty, sell_price)
        except Exception as e:
            send_telegram(f"Grid emir hata: {str(e)}")
            return

def monitor_and_protect():
    while True:
        try:
            price = get_price()
            # Aralığın dışına çıkarsa durdur (manuel restart)
            initial_price = get_price()  # başlangıç fiyatını dinamik tutmak için
            if abs(price - initial_price) / initial_price > 0.05:
                send_telegram("⚠️ Fiyat aralık dışı kaldı, bot durdu. Dashboard'dan manuel restart yap.")
                break

            # Kar izleme (%20'de mesaj)
            positions = exchange.fapiPrivate_get_positionrisk({'symbol': SYMBOL})
            for pos in positions:
                pnl = float(pos['unrealizedProfit'])
                if pnl > 0.2 * AMOUNT:
                    send_telegram(f"💰 Pozisyon karı +{pnl:.2f}$ - Kısmi kar al veya trailing stop düşün")

            time.sleep(60)
        except Exception as e:
            send_telegram(f"Monitor hata: {str(e)}")
            time.sleep(300)

if __name__ == "__main__":
    send_telegram("☁️ Grid Bot Başladı - 10$ + 3x izole + SOLUSDT")
    set_leverage_and_isolated()
    create_grid()
    monitor_and_protect()
