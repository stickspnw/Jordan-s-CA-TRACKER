import telebot
import json
import time

# Load config
with open("config.py") as f:
    exec(f.read())

bot = telebot.TeleBot(BOT_TOKEN)

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "🟢 CA Tracker Bot is running!")

# Simple loop to keep it alive
if __name__ == "__main__":
    try:
        print("Bot is starting...")
        bot.polling(non_stop=True)
    except Exception as e:
        print(f"Error: {e}")
