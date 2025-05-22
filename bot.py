import os
import threading
from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

BOT_TOKEN = os.environ.get("BOT_TOKEN", "7547000913:AAHGQNzoUHR2bqKOFJn5AHuNPaqAHd-JqSs")
ADMIN_ID = 1999452367
CHANNEL_USERNAME = "@LootLeloDeals"
AMAZON_TAG = "yourtag-21"
FLIPKART_TAG = "yourtag"

def convert_link(link: str) -> str:
    if "amazon." in link and "tag=" not in link:
        return f"{link}&tag={AMAZON_TAG}" if "?" in link else f"{link}?tag={AMAZON_TAG}"
    if "flipkart." in link and "affid=" not in link:
        return f"{link}&affid={FLIPKART_TAG}" if "?" in link else f"{link}?affid={FLIPKART_TAG}"
    return link

def extract_link(text: str) -> str:
    for word in text.split():
        if "amazon." in word or "flipkart." in word:
            return convert_link(word)
    return None

def format_message(text: str, category: str) -> str:
    return f"""
🔥 **{category} Deal Alert!**

{text}

⏳ Hurry before it's gone!
""".strip()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Welcome to **LootLelo Bot**!\nUse /adddeal or /electronics to post.", parse_mode="Markdown")

async def post_deal(update: Update, context: ContextTypes.DEFAULT_TYPE, category: str):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("❌ You are not authorized.")
        return

    text = " ".join(context.args)
    if not text:
        await update.message.reply_text("⚠️ Please add text.\nExample:\n`/adddeal 90% off - https://amzn.to/deal`", parse_mode="Markdown")
        return

    link = extract_link(text)
    buttons = InlineKeyboardMarkup([[InlineKeyboardButton("🛒 Buy Now", url=link)]]) if link else None
    msg = format_message(text, category)

    await update.message.reply_text(msg, parse_mode="Markdown", reply_markup=buttons)
    await context.bot.send_message(chat_id=CHANNEL_USERNAME, text=msg, parse_mode="Markdown", reply_markup=buttons)

async def photo_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return

    caption = update.message.caption or ""
    link = extract_link(caption)
    buttons = InlineKeyboardMarkup([[InlineKeyboardButton("🛒 Buy Now", url=link)]]) if link else None
    msg = format_message(caption, "General")

    await context.bot.send_photo(chat_id=CHANNEL_USERNAME, photo=update.message.photo[-1].file_id, caption=msg, parse_mode="Markdown", reply_markup=buttons)

async def adddeal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await post_deal(update, context, "General")

async def electronics(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await post_deal(update, context, "Electronics")

async def fashion(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await post_deal(update, context, "Fashion")

async def grocery(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await post_deal(update, context, "Grocery")

def run_bot():
    application = ApplicationBuilder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("adddeal", adddeal))
    application.add_handler(CommandHandler("electronics", electronics))
    application.add_handler(CommandHandler("fashion", fashion))
    application.add_handler(CommandHandler("grocery", grocery))
    application.add_handler(MessageHandler(filters.PHOTO, photo_handler))
    print("Bot is running...")
    application.run_polling()

threading.Thread(target=run_bot).start()

app = Flask(__name__)

@app.route('/')
def home():
    return "LootLelo bot is running on Render!"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
    
