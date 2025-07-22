import telebot
import json
import time
from solana.rpc.api import Client

# --- CONFIGURATION ---
with open("config.py") as f:
    exec(f.read())

bot = telebot.TeleBot(BOT_TOKEN)

# --- WALLET LOADING ---
def load_wallets():
    try:
        with open("wallets.json", "r") as f:
            return json.load(f)
    except:
        return {}

wallets = load_wallets()

# --- COMMAND: /start ---
@bot.message_handler(commands=["start"])
def start(message):
    bot.reply_to(message, "👋 Bot online. Send /menu to manage your wallet.")

# --- COMMAND: /menu ---
@bot.message_handler(commands=["menu"])
def menu(message):
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("📥 Create Wallet", "📤 Withdraw")
    markup.row("📃 My Wallet", "📲 Delete Wallet")
    bot.send_message(message.chat.id, "Choose an option:", reply_markup=markup)

# --- ACTION: Create Wallet ---
@bot.message_handler(func=lambda msg: msg.text == "📥 Create Wallet")
def create_wallet(message):
    from solders.keypair import Keypair
    kp = Keypair()
    wallets[str(message.chat.id)] = {
        "public": str(kp.pubkey()),
        "secret": list(kp.secret())
    }
    with open("wallets.json", "w") as f:
        json.dump(wallets, f)
    bot.send_message(message.chat.id, f"✅ New Solana Wallet Created:\n{kp.pubkey()}")

# --- ACTION: My Wallet ---
@bot.message_handler(func=lambda msg: msg.text == "📃 My Wallet")
def my_wallet(message):
    wallet = wallets.get(str(message.chat.id))
    if wallet:
        bot.send_message(message.chat.id, f"💼 Your Wallet:\n{wallet['public']}")
    else:
        bot.send_message(message.chat.id, "❌ No wallet found. Use 📥 Create Wallet.")

# --- ACTION: Delete Wallet ---
@bot.message_handler(func=lambda msg: msg.text == "📲 Delete Wallet")
def delete_wallet(message):
    if str(message.chat.id) in wallets:
        del wallets[str(message.chat.id)]
        with open("wallets.json", "w") as f:
            json.dump(wallets, f)
        bot.send_message(message.chat.id, "🗑️ Wallet deleted.")
    else:
        bot.send_message(message.chat.id, "❌ No wallet to delete.")

# --- ACTION: Withdraw (mock for now) ---
@bot.message_handler(func=lambda msg: msg.text == "📤 Withdraw")
def withdraw(message):
    bot.send_message(message.chat.id, "💸 Withdrawal system coming soon.")

# --- Start polling ---
print("🤖 Bot running...")
bot.infinity_polling()
