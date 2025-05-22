from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# CONFIGURATION
BOT_TOKEN = "7547000913:AAHGQNzoUHR2bqKOFJn5AHuNPaqAHd-JqSs"
ADMIN_ID = 1999452367
CHANNEL_USERNAME = "@LootLeloDeals"
AMAZON_TAG = "yourtag-21"  # Replace this with your actual Amazon affiliate tag
FLIPKART_TAG = "yourtag"   # Replace this with your Flipkart affiliate tag

# AFFILIATE LINK CONVERTER
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
    return f"""🔥 **{category} Deal Alert!**

{text}

⏳ Hurry before it's gone!
""".strip()

# COMMAND HANDLERS
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

# PHOTO HANDLER
async def photo_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return

    caption = update.message.caption or ""
    link = extract_link(caption)
    buttons = InlineKeyboardMarkup([[InlineKeyboardButton("🛒 Buy Now", url=link)]]) if link else None
    msg = format_message(caption, "General")

    await context.bot.send_photo(chat_id=CHANNEL_USERNAME, photo=update.message.photo[-1].file_id, caption=msg, parse_mode="Markdown", reply_markup=buttons)

# CATEGORY COMMANDS
async def adddeal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await post_deal(update, context, "General")

async def electronics(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await post_deal(update, context, "Electronics")

async def fashion(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await post_deal(update, context, "Fashion")

async def grocery(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await post_deal(update, context, "Grocery")

# MAIN
if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("adddeal", adddeal))
    app.add_handler(CommandHandler("electronics", electronics))
    app.add_handler(CommandHandler("fashion", fashion))
    app.add_handler(CommandHandler("grocery", grocery))
    app.add_handler(MessageHandler(filters.PHOTO, photo_handler))
    print("Bot is running...")
    app.run_polling()
