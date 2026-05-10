import os
from flask import Flask
from threading import Thread
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters

# --- RENDER WEB SERVER (Keeping the bot alive) ---
app_flask = Flask('')

@app_flask.route('/')
def home():
    return "Bot is running 24/7!"

def run_web():
    app_flask.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run_web)
    t.start()

# ==============================
# CONFIGURATION
# ==============================
# Aapka Bot Token (Please keep this secret)
TOKEN = "8678651879:AAEPlTI-EmHXYLMrQginDWWQq3_dfAWv6eI" 
# Aapka User ID
ADMIN_ID =  8766444295
# Aapka Support Username
SUPPORT_USERNAME = "@CherryQueenTG"
# Aapka UPI ID
UPI_ID = "Q562574548@ybl"
# Demo Link
DEMO_LINK = "https://t.me/+cwlEHvWpayc4YmYx"

# Study Material Links (Replace these with your actual links)
PACK_LINKS = {
    "basic": "https://t.me/your_basic_pack_link",
    "premium": "https://t.me/your_premium_pack_link",
    "lifetime": "https://t.me/your_lifetime_pack_link"
}

# ==============================
# BOT FUNCTIONS
# ==============================

# Start Command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("📚 Buy Study Material", callback_data="buy_menu")],
        [InlineKeyboardButton("🎁 Demo Content", callback_data="demo")],
        [InlineKeyboardButton("📞 Support", callback_data="support")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    welcome_text = (
        "👋 *Welcome to KALPU STORE*\n\n"
        "Best quality Study Materials aur Notes yahan milenge.\n\n"
        "👇 Niche diye gaye buttons use karein:"
    )
    await update.message.reply_text(welcome_text, reply_markup=reply_markup, parse_mode="Markdown")

# Button Click Handler
async def handle_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "buy_menu":
        keyboard = [
            [InlineKeyboardButton("📘 Basic Pack - ₹99", callback_data="pay_basic")],
            [InlineKeyboardButton("🚀 Premium Pack - ₹299", callback_data="pay_premium")],
            [InlineKeyboardButton("👑 Lifetime Pack - ₹499", callback_data="pay_lifetime")],
            [InlineKeyboardButton("⬅️ Back", callback_data="main_menu")]
        ]
        await query.message.edit_text("✨ *Choose Your Pack:*", reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

    elif query.data == "main_menu":
        keyboard = [
            [InlineKeyboardButton("📚 Buy Study Material", callback_data="buy_menu")],
            [InlineKeyboardButton("🎁 Demo Content", callback_data="demo")],
            [InlineKeyboardButton("📞 Support", callback_data="support")]
        ]
        await query.message.edit_text("👇 Niche diye gaye buttons use karein:", reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

    elif query.data.startswith("pay_"):
        pack_name = query.data.split("_")[1]
        context.user_data['selected_pack'] = pack_name
        
        price = "99" if pack_name == "basic" else "299" if pack_name == "premium" else "499"
        
        payment_text = (
            f"💳 *PAYMENT FOR {pack_name.upper()} PACK*\n\n"
            f"💰 *Amount:* ₹{price}\n"
            f"📌 *UPI ID:* `{UPI_ID}`\n\n"
            "✅ *Steps:*\n"
            "1. QR code scan karein ya UPI ID copy karein.\n"
            "2. Payment karke uska *Screenshot* yahan bhejein.\n"
            "3. Admin verify karke material bhej dega."
        )
        
        try:
            await query.message.reply_photo(photo=open("qr.jpg", "rb"), caption=payment_text, parse_mode="Markdown")
        except FileNotFoundError:
            await query.message.reply_text(payment_text + "\n\n*(QR Code image missing, pay using UPI ID)*", parse_mode="Markdown")

    elif query.data == "demo":
        await query.message.reply_text(f"🎁 *DEMO MATERIAL:* \n{DEMO_LINK}", parse_mode="Markdown")

    elif query.data == "support":
        await query.message.reply_text(f"📞 *ADMIN SUPPORT:* {SUPPORT_USERNAME}", parse_mode="Markdown")

    # ADMIN ACTIONS (Approve/Reject)
    elif query.data.startswith("approve_"):
        _, user_id, pack = query.data.split("_")
        material_link = PACK_LINKS.get(pack, "Link not set.")
        
        # User ko link bhejna
        await context.bot.send_message(
            chat_id=int(user_id), 
            text=f"✅ *PAYMENT APPROVED!*\n\n📦 *Pack:* {pack.upper()}\n📥 *Download Material:* {material_link}", 
            parse_mode="Markdown"
        )
        # Admin button hatana
        await query.message.edit_caption(caption=f"✅ User {user_id} Approved for {pack}.")

    elif query.data.startswith("reject_"):
        _, user_id = query.data.split("_")
        await context.bot.send_message(chat_id=int(user_id), text="❌ *PAYMENT REJECTED!*\n\nInvalid screenshot ya payment nahi mili. Support se contact karein.", parse_mode="Markdown")
        await query.message.edit_caption(caption=f"❌ User {user_id} Rejected.")

# Handle Screenshot Photo
async def handle_screenshot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    pack = context.user_data.get('selected_pack', 'unknown')

    # Send to Admin
    admin_keyboard = [
        [InlineKeyboardButton("✅ Approve", callback_data=f"approve_{user.id}_{pack}")],
        [InlineKeyboardButton("❌ Reject", callback_data=f"reject_{user.id}")]
    ]
    
    admin_caption = (
        f"📩 *NEW PAYMENT RECEIVED*\n\n"
        f"👤 *User:* {user.first_name}\n"
        f"🆔 *ID:* `{user.id}`\n"
        f"📦 *Requested Pack:* {pack.upper()}"
    )
    
    await context.bot.send_photo(
        chat_id=ADMIN_ID,
        photo=update.message.photo[-1].file_id,
        caption=admin_caption,
        reply_markup=InlineKeyboardMarkup(admin_keyboard),
        parse_mode="Markdown"
    )

    await update.message.reply_text("✅ Screenshot mil gaya! Admin check kar raha hai, please wait.")

# ==============================
# MAIN RUNNER
# ==============================
if __name__ == '__main__':
    keep_alive() # Start Flask
    print("Bot is starting...")
    
    app = ApplicationBuilder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(handle_buttons))
    app.add_handler(MessageHandler(filters.PHOTO, handle_screenshot))
    
    app.run_polling()
