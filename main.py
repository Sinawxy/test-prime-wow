from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CallbackQueryHandler, CommandHandler, ContextTypes

# ======= توکن ربات =======
TOKEN = "8507768646:AAFlTACsPQ_lKN7N1qpONDkbkHpPzxbExZk"

# ======= تابع start =======
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("💠 سفارش بوست", callback_data='boost')],
        [InlineKeyboardButton("💰 خرید گلد", callback_data='gold')],
        [InlineKeyboardButton("ℹ️ اطلاعات خدمات", callback_data='info')],
        [InlineKeyboardButton("📜 قوانین و نکات امنیتی", callback_data='rules')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    if update.message:
        await update.message.reply_text(
            "سلام! به ربات Prime WoW خوش آمدی 😎\nلطفا یکی از گزینه‌ها را انتخاب کن:", 
            reply_markup=reply_markup
        )
    else:
        await update.callback_query.edit_message_text(
            "سلام! به ربات Prime WoW خوش آمدی 😎\nلطفا یکی از گزینه‌ها را انتخاب کن:", 
            reply_markup=reply_markup
        )

# ======= هندلر Callback =======
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "boost":
        await query.edit_message_text("💠 سفارش بوست انتخاب شد!")

    elif query.data == "gold":
        await query.edit_message_text("💰 خرید گلد انتخاب شد!")

    elif query.data == "info":
        await query.edit_message_text("ℹ️ خدمات ما شامل:\n- بوست 1 تا 80\n- خرید گلد\n- پشتیبانی سریع و امن")

    elif query.data == "rules":
        await query.edit_message_text("📜 قوانین:\n1. اکانت خود را امن نگه دارید\n2. پسورد خود را به هیچکس ندهید\n3. پس از سفارش، ادمین با شما تماس خواهد گرفت")

# ======= Main =======
if __name__ == "__main__":
    app = Application.builder().token(TOKEN).build()  # سازگار با Python 3.13
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button))
    print("Bot is running...")
    app.run_polling()
