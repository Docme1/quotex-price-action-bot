import telebot
import time

TOKEN = "YOUR_BOT_TOKEN"

bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(
        message,
        "Welcome to Price Action Signal Bot!\n"
        "Bot is online.\n"
        "OTC + LIVE Market Analysis Coming Soon."
    )

@bot.message_handler(commands=['help'])
def help(message):
    bot.reply_to(message, "Price Action Bot is running.")

print("Bot Started...")

bot.infinity_polling()
