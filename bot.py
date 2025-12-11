import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    MessageHandler, ContextTypes, filters
)

# === Настройки ===
BOT_TOKEN = os.getenv("BOT_TOKEN")
GROUP_CHAT_ID = -1003462107945  # ID твоей приватной группы

if not BOT_TOKEN:
    raise ValueError("❌ Переменная BOT_TOKEN не задана!")

# === Логирование ===
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

# === Каталог духов ===
PERFUMES = [
    {"name": "Baccarat Rouge 540", "volumes": [6,10,20,30,50,100], "prices": [300,800,1200,1500,2100,4000]},
    {"name": "Antonio Banderas", "volumes": [6,10,20,30,50,100], "prices": [350,900,1300,1800,2100,4000]},
    {"name": "Tom Ford - Tobacco Vanille", "volumes": [6,10,20,30,50,100], "prices": [300,850,1250,1700,2150,4000]},
    {"name": "Marc-Antoine Barrois", "volumes": [6,10,20,30,50,100], "prices": [300,800,1200,1600,2200,4200]},
    {"name": "Paco Rabanne - Invictus", "volumes": [6,10,20,30,50,100], "prices": [300,850,1300,1800,2100,4000]},
    {"name": "Black Opium", "volumes": [6,10,20,30,50,100], "prices": [300,850,1200,1900,2100,4000]},
    {"name": "Attar Hayati", "volumes": [6,10,20,30,50,100], "prices": [300,900,1400,1600,2100,4100]},
    {"name": "Tom Ford - Lost Cherry", "volumes": [6,10,20,30,50,100], "prices": [400,850,1300,1800,2100,4000]},
    {"name": "Tiziana Terenzi - Cassiopea", "volumes": [6,10,20,30,50,100], "prices": [350,800,1100,1500,2150,4200]},
    {"name": "Lacoste - Eau de Lacoste", "volumes": [6,10,20,30,50,100], "prices": [300,850,1000,1750,2150,4200]},
    {"name": "Chanel No.5", "volumes": [6,10,20,30,50,100], "prices": [300,850,1350,1500,2000,4000]},
    {"name": "Eclaf - Spart Molecule", "volumes": [6,10,20,30,50,100], "prices": [300,900,1100,1800,2200,4300]},
    {"name": "Molecule - Pink 090.09", "volumes": [6,10,20,30,50,100], "prices": [300,850,1300,1600,2200,4300]},
    {"name": "Nefertiti", "volumes": [6,10,20,30,50,100], "prices": [300,850,1400,1600,2100,4000]},
    {"name": "Игры разума", "volumes": [6,10,20,30,50,100], "prices": [350,900,1200,1900,2100,4000]},
    {"name": "Zielinski & Rozen - Vanilla Blend", "volumes": [6,10,20,30,50,100], "prices": [300,800,1200,1500,2100,4000]},
    {"name": "Victoria's Secret - Eau So", "volumes": [6,10,20,30,50,100], "prices": [350,900,1300,1800,2200,4300]},
    {"name": "Ex Nihilo - Fleur Narcotique", "volumes": [6,10,20,30,50,100], "prices": [300,850,1250,1700,2200,4300]},
    {"name": "Индивидуальный заказ (любые духи)", "volumes": [6,10,20,30,50,100], "prices": [300,850,1250,1700,2200,4300]},
]

# === Хранилище ===
user_carts = {}
user_phones = {}

def get_cart(user_id):
    return user_carts.get(user_id, [])

def add_to_cart(user_id, perfume_index, volume):
    if user_id not in user_carts:
        user_carts[user_id] = []
    p = PERFUMES[perfume_index]
    price = p["prices"][p["volumes"].index(volume)]
    user_carts[user_id].append({"perfume_index": perfume_index, "volume": volume, "price": price})

def clear_cart(user_id):
    user_carts.pop(user_id, None)
    user_phones.pop(user_id, None)

def format_cart(user_id):
    cart = get_cart(user_id)
    if not cart:
        return "🛒 Ваша корзина пуста."
    lines = []
    total = 0
    for i, item in enumerate(cart):
        p = PERFUMES[item["perfume_index"]]
        lines.append(f"{i+1}. {p['name']} — {item['volume']} мл — {item['price']} ₽")
        total += item["price"]
    return "🛒 Ваш заказ:\n" + "\n".join(lines) + f"\n\nИтого: {total} ₽"

# === Обработчики ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("Ароматы", callback_data="show_perfumes")],
        [InlineKeyboardButton("🛒 Корзина", callback_data="view_cart")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "👋 Добро пожаловать в Main Perfume!\nРазлив от 6 мл до 100 мл. Цены от 300 до 4300 ₽.",
        reply_markup=reply_markup
    )

async def show_perfumes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    keyboard = [[InlineKeyboardButton(p["name"], callback_data=f"perfume_{i}")] for i, p in enumerate(PERFUMES)]
    keyboard.append([InlineKeyboardButton("↩️ Назад", callback_data="back_to_menu")])
    await query.edit_message_text("Выберите аромат:", reply_markup=InlineKeyboardMarkup(keyboard))

async def show_volumes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    idx = int(query.data.split("_")[1])
    p = PERFUMES[idx]
    keyboard = [
        [InlineKeyboardButton(f"{vol} мл — {price} ₽", callback_data=f"add_{idx}_{vol}")]
        for vol, price in zip(p["volumes"], p["prices"])
    ]
    keyboard.append([InlineKeyboardButton("↩️ Назад к ароматам", callback_data="show_perfumes")])
    await query.edit_message_text(f"Аромат: *{p['name']}*\nВыберите объём:", 
                                  reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

async def add_to_cart_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    _, idx, vol = query.data.split("_")
    add_to_cart(update.effective_user.id, int(idx), int(vol))
    await query.edit_message_text(
        "✅ Добавлено в корзину!",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🛒 Корзина", callback_data="view_cart")],
            [InlineKeyboardButton("Ароматы", callback_data="show_perfumes")]
        ])
    )

async def view_cart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = update.effective_user.id
    cart_text = format_cart(user_id)
    keyboard = []
    if get_cart(user_id):
        for i in range(len(get_cart(user_id))):
            keyboard.append([InlineKeyboardButton(f"Удалить позицию {i+1}", callback_data=f"remove_{i}")])
        keyboard.append([InlineKeyboardButton("🗑 Очистить корзину", callback_data="clear_cart")])
        keyboard.append([InlineKeyboardButton("✅ Оформить заказ", callback_data="checkout")])
    keyboard.append([InlineKeyboardButton("↩️ Назад", callback_data="back_to_menu")])
    await query.edit_message_text(cart_text, reply_markup=InlineKeyboardMarkup(keyboard))

async def remove_item(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = update.effective_user.id
    idx = int(query.data.split("_")[1])
    cart = user_carts.get(user_id)
    if cart and 0 <= idx < len(cart):
        cart.pop(idx)
    await view_cart(update, context)

async def clear_cart_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    clear_cart(update.effective_user.id)
    await query.edit_message_text("Корзина очищена.", 
                                  reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("↩️ Назад", callback_data="back_to_menu")]]))

async def checkout(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = update.effective_user.id
    if not get_cart(user_id):
        await query.edit_message_text("Корзина пуста.")
        return

    # Просим отправить номер телефона
    keyboard = [[KeyboardButton("📱 Отправить номер", request_contact=True)]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
    await query.message.reply_text(
        "Пожалуйста, отправьте ваш номер телефона для связи:",
        reply_markup=reply_markup
    )
    await query.message.delete()

# === Обработка номера телефона ===
async def handle_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    contact = update.message.contact
    if not contact:
        await update.message.reply_text("Пожалуйста, используйте кнопку 📱 Отправить номер.")
        return

    user_id = update.effective_user.id
    phone = contact.phone_number
    user_phones[user_id] = phone

    # Отправляем заказ в группу
    user = update.effective_user
    cart_text = format_cart(user_id)
    order_msg = (
        f"📦 НОВЫЙ ЗАКАЗ\n\n"
        f"👤 Имя: {user.full_name}\n"
        f"🆔 ID: {user.id}\n"
        f"✉️ Юзернейм: @{user.username if user.username else '—'}\n"
        f"📞 Телефон: +{phone}\n\n"
        f"{cart_text.replace('🛒 Ваш заказ:', '📦 Товары:')}"
    )

    try:
        await context.bot.send_message(chat_id=GROUP_CHAT_ID, text=order_msg)
        clear_cart(user_id)
        await update.message.reply_text(
            "✅ Заказ оформлен!\nС вами свяжутся в ближайшее время.",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("↩️ В меню", callback_data="back_to_menu")]])
        )
    except Exception as e:
        logging.error(f"Ошибка отправки заказа: {e}")
        await update.message.reply_text("❌ Не удалось отправить заказ. Попробуйте позже.")

async def back_to_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await start(query, context)

# === Запуск ===
import asyncio

async def run_bot():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(show_perfumes, pattern="^show_perfumes$"))
    app.add_handler(CallbackQueryHandler(show_volumes, pattern=r"^perfume_\d+$"))
    app.add_handler(CallbackQueryHandler(add_to_cart_handler, pattern=r"^add_\d+_\d+$"))
    app.add_handler(CallbackQueryHandler(view_cart, pattern="^view_cart$"))
    app.add_handler(CallbackQueryHandler(remove_item, pattern=r"^remove_\d+$"))
    app.add_handler(CallbackQueryHandler(clear_cart_handler, pattern="^clear_cart$"))
    app.add_handler(CallbackQueryHandler(checkout, pattern="^checkout$"))
    app.add_handler(CallbackQueryHandler(back_to_menu, pattern="^back_to_menu$"))
    app.add_handler(MessageHandler(filters.CONTACT, handle_phone))

    await app.initialize()
    await app.start()
    await app.updater.start_polling()
    await asyncio.Event().wait()

def main():
    asyncio.run(run_bot())

if __name__ == "__main__":
    main()