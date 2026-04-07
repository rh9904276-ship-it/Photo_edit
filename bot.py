from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
import requests
from PIL import Image, ImageEnhance

BOT_TOKEN = "8734269414:AAGnGrAxIZZnje4_5O6d2mN9iaM_m25xlDE"
CHANNEL_USERNAME = "@saniedit9"
API_KEY = "2425ee33-841b-4853-bfdb-122b20d8d6d7"

user_mode = {}

# 🔐 Check join
async def is_joined(user_id, bot):
    try:
        member = await bot.get_chat_member(CHANNEL_USERNAME, user_id)
        return member.status in ["member", "administrator", "creator"]
    except:
        return False

# 🚀 Start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id

    if not await is_joined(user_id, context.bot):
        keyboard = [
            [InlineKeyboardButton("📢 Channel Join", url=f"https://t.me/{CHANNEL_USERNAME[1:]}")],
            [InlineKeyboardButton("✅ Joined", callback_data="check_join")]
        ]
        await update.message.reply_text(
            "❌ আগে channel join করো!",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return

    text = """👋 স্বাগতম!

🤖 Bot তৈরি করেছে: Sani Islam  
🎯 কাজ: ছবি Enhance + Phone Style Effect

👇 নিচে option select করো:
"""

    keyboard = [
        [InlineKeyboardButton("🖼 Enhance", callback_data='enhance')],
        [InlineKeyboardButton("🍎 iPhone Style", callback_data='iphone')],
        [InlineKeyboardButton("📱 Samsung Style", callback_data='samsung')],
        [InlineKeyboardButton("🎨 Cartoon", callback_data='cartoon')]
    ]

    await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard))

# ✅ Join check button
async def check_join(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id

    if await is_joined(user_id, context.bot):
        await query.message.reply_text("✅ এখন bot use করতে পারো! /start দাও")
    else:
        await query.message.reply_text("❌ এখনো join করো নাই!")

# 🎛 Button handler
async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    user_mode[user_id] = query.data
    await query.message.reply_text("📸 এখন ছবি পাঠাও")

# 🖼 Style functions
def iphone_style(path):
    img = Image.open(path)
    img = ImageEnhance.Color(img).enhance(1.1)
    img = ImageEnhance.Brightness(img).enhance(1.05)
    img.save("out.jpg")
    return "out.jpg"

def samsung_style(path):
    img = Image.open(path)
    img = ImageEnhance.Color(img).enhance(1.4)
    img = ImageEnhance.Sharpness(img).enhance(1.8)
    img.save("out.jpg")
    return "out.jpg"

# 📸 Handle photo
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id

    if user_id not in user_mode:
        await update.message.reply_text("❗ আগে option select করো")
        return

    mode = user_mode[user_id]

    photo = update.message.photo[-1]
    file = await photo.get_file()
    path = await file.download_to_drive()

    await update.message.reply_text("⏳ Processing...")

    if mode == "enhance":
        with open(path, 'rb') as f:
            res = requests.post(
                "https://api.deepai.org/api/torch-srgan",
                files={'image': f},
                headers={'api-key': API_KEY}
            )
        output = res.json()["output_url"]
        await update.message.reply_photo(output)

    elif mode == "cartoon":
        with open(path, 'rb') as f:
            res = requests.post(
                "https://api.deepai.org/api/toonify",
                files={'image': f},
                headers={'api-key': API_KEY}
            )
        output = res.json()["output_url"]
        await update.message.reply_photo(output)

    elif mode == "iphone":
        out = iphone_style(path)
        await update.message.reply_photo(open(out, 'rb'))

    elif mode == "samsung":
        out = samsung_style(path)
        await update.message.reply_photo(open(out, 'rb'))

# ▶️ Run
app = ApplicationBuilder().token(BOT_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(check_join, pattern="check_join"))
app.add_handler(CallbackQueryHandler(button_click))
app.add_handler(MessageHandler(filters.PHOTO, handle_photo))

app.run_polling()
