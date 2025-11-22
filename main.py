import sqlite3
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CallbackQueryHandler, CommandHandler, ContextTypes

TOKEN = "8507768646:AAFlTACsPQ_lKN7N1qpONDkbkHpPzxbExZk"

# ======= دیتابیس برای ذخیره سفارش‌ها =======
conn = sqlite3.connect("orders.db")
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS orders
             (user_id INTEGER, order_type TEXT, start_level INTEGER, end_level INTEGER, gold_amount INTEGER, price REAL)''')
conn.commit()

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
        await update.message.reply_text("سلام! به ربات Prime WoW خوش اومدی 😎\nلطفا یکی از گزینه‌ها رو انتخاب کن:", reply_markup=reply_markup)
    else:
        await update.callback_query.edit_message_text("سلام! به ربات Prime WoW خوش اومدی 😎\nلطفا یکی از گزینه‌ها رو انتخاب کن:", reply_markup=reply_markup)

# ======= محاسبه قیمت بوست =======
def calculate_boost_price(start_level, end_level):
    base_price = 15000  # قیمت کل از 1 تا 80
    # نسبت تصاعدی: هر لول بالاتر هزینه بیشتری داره
    total_levels = 80 - 1
    selected_levels = end_level - start_level + 1
    price = base_price * (selected_levels / total_levels)
    return round(price, 2)

# ======= هندلر Callback =======
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    await query.answer()
    
    # منو اصلی
    if query.data == "boost":
        keyboard = [[InlineKeyboardButton(str(i), callback_data=f"boost_start_{i}")] for i in range(1, 81)]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text("💠 سفارش بوست:\nلطفا **سطح شروع** را انتخاب کن:", reply_markup=reply_markup)
    
    elif query.data.startswith("boost_start_"):
        start_level = int(query.data.split("_")[-1])
        context.user_data['boost_start'] = start_level
        keyboard = [[InlineKeyboardButton(str(i), callback_data=f"boost_end_{i}")] for i in range(start_level, 81)]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(f"سطح شروع: {start_level}\nلطفا **سطح پایان** را انتخاب کن:", reply_markup=reply_markup)
    
    elif query.data.startswith("boost_end_"):
        end_level = int(query.data.split("_")[-1])
        start_level = context.user_data.get('boost_start', 1)
        price = calculate_boost_price(start_level, end_level)
        context.user_data['boost_end'] = end_level
        context.user_data['boost_price'] = price
        
        keyboard = [[InlineKeyboardButton("تایید سفارش ✅", callback_data="boost_confirm")],
                    [InlineKeyboardButton("بازگشت 🔙", callback_data="start")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(f"✅ سفارش شما:\nسطح {start_level} تا {end_level}\nقیمت: {price}k\n\nتایید می‌کنید؟", reply_markup=reply_markup)
    
    elif query.data == "boost_confirm":
        start_level = context.user_data['boost_start']
        end_level = context.user_data['boost_end']
        price = context.user_data['boost_price']
        c.execute("INSERT INTO orders VALUES (?,?,?,?,?,?)", (user_id, 'boost', start_level, end_level, None, price))
        conn.commit()
        await query.edit_message_text(f"🎉 سفارش بوست شما ثبت شد!\nسطح {start_level} تا {end_level}\nقیمت: {price}k\nادمین به زودی با شما تماس خواهد گرفت.")
    
    elif query.data == "gold":
        keyboard = [[InlineKeyboardButton(str(i*1000), callback_data=f"gold_amount_{i*1000}")] for i in range(1, 21)]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text("💰 خرید گلد:\nلطفا مقدار گلد مورد نظر خود را انتخاب کنید:", reply_markup=reply_markup)
    
    elif query.data.startswith("gold_amount_"):
        gold_amount = int(query.data.split("_")[-1])
        price = round(gold_amount / 1000 * 50, 2)  # مثال: هر 1000 گلد = 50k
        c.execute("INSERT INTO orders VALUES (?,?,?,?,?,?)", (user_id, 'gold', None, None, gold_amount, price))
        conn.commit()
        await query.edit_message_text(f"🎉 سفارش گلد شما ثبت شد!\nمقدار: {gold_amount}\nقیمت: {price}k\nادمین به زودی با شما تماس خواهد گرفت.")
    
    elif query.data == "info":
        await query.edit_message_text("ℹ️ خدمات ما شامل:\n- بوست 1 تا 80\n- خرید گلد\n- پشتیبانی سریع و امن")
    
    elif query.data == "rules":
        await query.edit_message_text("📜 قوانین:\n1. اکانت خود را امن نگه دارید\n2. پسورد خود را به هیچکس ندهید\n3. پس از سفارش، ادمین با شما تماس خواهد گرفت")
    
    elif query.data == "start":
        await start(update, context)

# ======= Main =======
if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button))
    print("Bot is running...")
    app.run_polling()
