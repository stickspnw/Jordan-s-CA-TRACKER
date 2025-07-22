import logging
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, CallbackQueryHandler, MessageHandler, filters
from config import BOT_TOKEN, FEE_WALLET, SOLANA_RPC
from utils import create_wallet, get_balance, send_sol, format_usd_value, tracked_tweets, tracked_wallets

user_wallets = {}
user_fee_log = {}

logging.basicConfig(level=logging.INFO)

# Main menu buttons
def get_main_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📦 New Wallet", callback_data="new_wallet"),
         InlineKeyboardButton("🗑️ Delete Wallet", callback_data="delete_wallet")],
        [InlineKeyboardButton("💰 Balance", callback_data="balance"),
         InlineKeyboardButton("💸 Withdraw", callback_data="withdraw")],
        [InlineKeyboardButton("🟢 Buy", callback_data="buy"),
         InlineKeyboardButton("🔴 Sell", callback_data="sell")],
        [InlineKeyboardButton("📡 Feed", callback_data="feed"),
         InlineKeyboardButton("⚙️ Settings", callback_data="settings")]
    ])

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Welcome to the CA Tracker Bot!\n\n"
        "You can track wallets, buy/sell, and manage your SOL with ease.\n"
        "Use the buttons below to get started.",
        reply_markup=get_main_menu()
    )

async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📲 Menu", reply_markup=get_main_menu())

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    await query.answer()

    if query.data == "new_wallet":
        pub, priv = create_wallet()
        user_wallets[user_id] = {"public": pub, "private": priv}
        await query.edit_message_text(f"✅ New wallet created:\n`{pub}`", parse_mode='Markdown')

    elif query.data == "delete_wallet":
        user_wallets.pop(user_id, None)
        await query.edit_message_text("🗑️ Wallet deleted.")

    elif query.data == "balance":
        wallet = user_wallets.get(user_id)
        if not wallet:
            await query.edit_message_text("❌ No wallet found.")
            return
        sol = get_balance(wallet["public"])
        usd = format_usd_value(sol)
        await query.edit_message_text(f"💰 Balance: {sol} SOL (~${usd})", reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔄 Refresh", callback_data="balance")]
        ]))

    elif query.data == "withdraw":
        await query.edit_message_text("💸 Send me the wallet address to withdraw to.")
        context.user_data["awaiting_withdraw"] = True

    elif query.data == "buy":
        await query.edit_message_text("🟢 How much SOL to buy with?")

    elif query.data == "sell":
        await query.edit_message_text("🔴 How much SOL to sell?")

    elif query.data == "feed":
        alerts = tracked_wallets() + tracked_tweets()
        feed_msg = "📡 Recent Alerts:\n\n" + "\n".join(alerts[-15:])
        await query.edit_message_text(feed_msg or "No alerts yet.", reply_markup=get_main_menu())

    elif query.data == "settings":
        await query.edit_message_text("⚙️ Settings are coming soon!", reply_markup=get_main_menu())

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    text = update.message.text

    if context.user_data.get("awaiting_withdraw"):
        context.user_data["awaiting_withdraw"] = False
        wallet = user_wallets.get(user_id)
        if not wallet:
            await update.message.reply_text("❌ No wallet.")
            return
        amount = get_balance(wallet["public"])
        fee = round(amount * 0.0075, 5)
        final_amount = round(amount - fee, 5)
        tx = send_sol(wallet["private"], text, final_amount)
        send_sol(wallet["private"], FEE_WALLET, fee)
        user_fee_log[user_id] = user_fee_log.get(user_id, 0) + fee
        await update.message.reply_text(f"✅ Sent {final_amount} SOL (fee: {fee})\nTx: {tx}")

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("menu", menu))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    app.run_polling()

if __name__ == "__main__":
    main()
