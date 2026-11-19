import os
import time
import requests
import telebot

TOKEN = os.getenv("BOT_TOKEN")

if not TOKEN:
    raise ValueError("BOT_TOKEN missing!")

bot = telebot.TeleBot(TOKEN)

BINANCE_URL = "https://api.binance.com/api/v3/klines"


def get_candles():
    response = requests.get(
        BINANCE_URL,
        params={
            "symbol": "BTCUSDT",
            "interval": "1m",
            "limit": 100
        },
        timeout=15
    )
    response.raise_for_status()
    return response.json()


def analyze_market():
    candles = get_candles()

    closes = [float(c[4]) for c in candles]
    opens = [float(c[1]) for c in candles]
    highs = [float(c[2]) for c in candles]
    lows = [float(c[3]) for c in candles]

    last = closes[-1]

    ema_fast = sum(closes[-9:]) / 9
    ema_slow = sum(closes[-21:]) / 21

    bullish = closes[-1] > opens[-1]
    bearish = closes[-1] < opens[-1]

    signal = "WAIT"
    reason = "Clear setup nahi mila."

    if ema_fast > ema_slow and bullish:
        signal = "CALL"
        reason = "Short-term trend bullish aur candle bullish hai."

    elif ema_fast < ema_slow and bearish:
        signal = "PUT"
        reason = "Short-term trend bearish aur candle bearish hai."

    return (
        f"BTC/USDT LIVE ANALYSIS\n\n"
        f"Price: {last}\n"
        f"1-minute signal: {signal}\n"
        f"Reason: {reason}\n\n"
        f"Data: Binance LIVE\n"
        f"Note: Signal guaranteed nahi hai."
    )


@bot.message_handler(commands=["start"])
def start(message):
    bot.reply_to(
        message,
        "Welcome to Price Action Bot!\n\n"
        "Commands:\n"
        "/signal - Market analysis\n"
        "/help - Help"
    )


@bot.message_handler(commands=["signal"])
def signal(message):
    try:
        bot.reply_to(message, analyze_market())
    except Exception as e:
        bot.reply_to(message, f"Data error: {e}")


@bot.message_handler(commands=["help"])
def help_command(message):
    bot.reply_to(
        message,
        "/signal bhejein BTC/USDT analysis ke liye."
    )


print("Bot Started...")
bot.infinity_polling()
