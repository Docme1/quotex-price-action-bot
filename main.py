import os
import requests
import telebot

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


print("Quotex Bot Started...")
bot.infinity_polling()
