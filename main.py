import os
import requests
import telebot
import threading
import time
from market_qx_candles import MarketQX
TOKEN = os.getenv("BOT_TOKEN")
API_KEY = os.getenv("OTCHARTS_API_KEY")

if not TOKEN:
    raise ValueError("BOT_TOKEN missing!")

if not API_KEY:
    raise ValueError("OTCHARTS_API_KEY missing!")

bot = telebot.TeleBot(TOKEN)

BASE_URL = "https://otcharts.com"

HEADERS = {
    "Authorization": f"Bearer {API_KEY}"
}


def test_api():
    response = requests.get(
        f"{BASE_URL}/v1/venues",
        headers=HEADERS,
        timeout=20
    )

    response.raise_for_status()

    data = response.json()

    venues = data.get("venues", [])

    quotex = next(
        (v for v in venues if v.get("id") == "quotex"),
        None
    )

    if not quotex:
        return "Quotex venue not found!"

    if not quotex.get("open"):
        return "Quotex API access is not open!"

    return "OTCharts connected!\nQuotex access: OPEN"


@bot.message_handler(commands=["start"])
def start(message):
    bot.reply_to(
        message,
        "Welcome to Quotex Price Action Bot!\n\n"
        "/testapi - Test OTCharts connection\n"
        "/signal - Signal status"
    )


@bot.message_handler(commands=["testapi"])
def test(message):
    try:
        bot.reply_to(message, test_api())
    except Exception as e:
        bot.reply_to(message, f"API Error: {e}")


@bot.message_handler(commands=["signal"])
def signal(message):
    bot.reply_to(
        message,
        "Market data verification pending.\n"
        "No signal generated yet."
    )
@bot.message_handler(commands=["testfeed"])
def testfeed(message):

    def check_feed():
        qx = None
        try:
            bot.reply_to(message, "Live OTC feed check ho raha hai...")

            qx = MarketQX().connect(wait_instruments=20)

            assets = [
                a for a in qx.instruments
                if "usdjpy" in a.lower() and "otc" in a.lower()
            ]

            if not assets:
                bot.reply_to(message, "USDJPY OTC pair feed mein nahi mila.")
                return

            asset = assets[0]
            received = threading.Event()
            result = {}

            def on_tick(a, ts, price, *args):
                if a == asset:
                    result["price"] = price
                    received.set()

            qx.on_tick(on_tick)
            qx.follow(asset, 60)

            if received.wait(20):
                bot.reply_to(
                    message,
                    f"Live feed tick received!\n{asset}: {result['price']}\n"
                    "Price matching abhi verify nahi hui."
                )
            else:
                bot.reply_to(message, "Feed se live tick nahi mili.")

        except Exception as e:
            bot.reply_to(message, f"Feed error: {e}")
        finally:
            if qx:
                qx.close()

    threading.Thread(target=check_feed, daemon=True).start()

print("Quotex Bot Started...")
bot.infinity_polling()
