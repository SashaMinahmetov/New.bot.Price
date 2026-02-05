import os
import logging
import re
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
)
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
    ContextTypes,
    ConversationHandler,
)

# Получаем токен
TOKEN = os.getenv("TOKEN")

# Настройка логирования
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# --- СОСТОЯНИЯ ---
# Вместо кучи состояний, делаем основные режимы
(
    MODE_SHELF,      # Режим скидки
    MODE_NX,         # Режим N+X
    MODE_KG,         # Режим цены за КГ
    MODE_ORIGINAL,   # Режим обратного расчёта
    MODE_PRO,        # Режим PRO (меню)
    MODE_PRO_INPUT,  # Ввод данных для PRO функций
    SETTINGS,        # Настройки языка
) = range(7)

# --- ЛОКАЛИЗАЦИЯ ---
LOCALIZATION = {
    'ru': {
        # Кнопки меню
        'btn_shelf': "🏷 Скидка %",
        'btn_nx': "🎁 Акция N+X",
        'btn_kg': "⚖️ Цена за кг",
        'btn_orig': "🔙 Цена без скидки",
        'btn_pro': "🌟 PRO режим",
        'btn_settings': "⚙️ Язык",
        
        # Приветствия режимов
        'welcome': "👇 **Меню внизу.** Выберите режим расчёта:",
        'mode_shelf_active': "🏷 **Режим: Скидка %**\nВведите цену товара (например: `299`) или цену и скидку (например: `299 15`)",
        'mode_nx_active': "🎁 **Режим: Акция N+X**\nВведите: `Кол-во` `Бесплатно` `Цена 1 шт`\nПример: `2 1 49.90` (2+1, цена 49.90)",
        'mode_kg_active': "⚖️ **Режим: Цена за КГ**\nВведите: `Цена` `Вес (г)`\nПример: `135 400` (135 грн за 400 г)",
        'mode_orig_active': "🔙 **Режим: Узнать цену без скидки**\nВведите: `Цена со скидкой` `Процент`\nПример: `199 20`",
        'mode_pro_active': "🌟 **PRO Режим**\nВыберите функцию в меню выше:",
        
        # Ответы
        'ask_discount': "💰 Цена: **{price}** грн.\nВыберите скидку:",
        'res_shelf': "🏷 **{price}** -{disc}% = **{total}** грн\n🔻 Выгода: {diff} грн",
        'res_nx': "🎁 Акция {n}+{x}\n📦 Всего: {count} шт\n💰 Платите за {n}: {total_pay:.2f} грн\n✅ **1 шт = {unit:.2f} грн**\n📉 Реальная скидка: {real_disc:.1f}%",
        'res_kg': "⚖️ {weight}г = {price} грн\n📊 **1 кг = {kg_price} грн**\n📏 100 г = {g100} грн",
        'res_orig': "🔙 Если **{final}** это цена с -{disc}%:\n💰 Было до скидки: **{orig}** грн",
        
        # Ошибки
        'err_format': "⚠️ Неверный формат для этого режима.\n📝 Подсказка: {hint}",
        'err_num': "⚠️ Используйте только числа.",
        'saved': "✅ Язык изменен.",
        
        # PRO меню
        'pro_menu_text': "Выберите PRO функцию:",
        'pro_btn_auto': "🤖 Авто-детект",
        'pro_btn_fixed': "💸 Фикс. скидка (грн)",
        'pro_btn_loyal': "💳 Карта лояльности",
        'pro_btn_double': "🔁 Двойная скидка",
        'pro_btn_compare': "⚖️ Сравнить товары",
        'pro_btn_margin': "📊 Маржа",
    },
    'uk': {
        'btn_shelf': "🏷 Знижка %",
        'btn_nx': "🎁 Акція N+X",
        'btn_kg': "⚖️ Ціна за кг",
        'btn_orig': "🔙 Ціна без знижки",
        'btn_pro': "🌟 PRO режим",
        'btn_settings': "⚙️ Мова",
        
        'welcome': "👇 **Меню знизу.** Оберіть режим розрахунку:",
        'mode_shelf_active': "🏷 **Режим: Знижка %**\nВведіть ціну (наприклад: `299`) або ціну та знижку (наприклад: `299 15`)",
        'mode_nx_active': "🎁 **Режим: Акція N+X**\nВведіть: `Кіл-ть` `Безкоштовно` `Ціна 1 шт`\nПриклад: `2 1 49.90` (2+1, ціна 49.90)",
        'mode_kg_active': "⚖️ **Режим: Ціна за КГ**\nВведіть: `Ціна` `Вага (г)`\nПриклад: `135 400` (135 грн за 400 г)",
        'mode_orig_active': "🔙 **Режим: Дізнатись ціну без знижки**\nВведіть: `Ціна зі знижкою` `Відсоток`\nПриклад: `199 20`",
        'mode_pro_active': "🌟 **PRO Режим**\nОберіть функцію в меню вище:",
        
        'ask_discount': "💰 Ціна: **{price}** грн.\nОберіть знижку:",
        'res_shelf': "🏷 **{price}** -{disc}% = **{total}** грн\n🔻 Вигода: {diff} грн",
        'res_nx': "🎁 Акція {n}+{x}\n📦 Всього: {count} шт\n💰 Платите за {n}: {total_pay:.2f} грн\n✅ **1 шт = {unit:.2f} грн**\n📉 Реальна знижка: {real_disc:.1f}%",
        'res_kg': "⚖️ {weight}г = {price} грн\n📊 **1 кг = {kg_price} грн**\n📏 100 г = {g100} грн",
        'res_orig': "🔙 Якщо **{final}** це ціна з -{disc}%:\n💰 Було до знижки: **{orig}** грн",
        
        'err_format': "⚠️ Невірний формат для цього режиму.\n📝 Підказка: {hint}",
        'err_num': "⚠️ Використовуйте лише числа.",
        'saved': "✅ Мову змінено.",
        
        'pro_menu_text': "Оберіть PRO функцію:",
        'pro_btn_auto': "🤖 Авто-детект",
        'pro_btn_fixed': "💸 Фікс. знижка (грн)",
        'pro_btn_loyal': "💳 Картка лояльності",
        'pro_btn_double': "🔁 Подвійна знижка",
        'pro_btn_compare': "⚖️ Порівняти товари",
        'pro_btn_margin': "📊 Маржа",
    }
}

# --- КЛАВИАТУРЫ ---

def get_lang(context):
    return context.user_data.get('lang', 'ru')

def get_main_keyboard(lang_code):
    l = LOCALIZATION[lang_code]
    return ReplyKeyboardMarkup(
        [
            [l['btn_shelf'], l['btn_kg']], 
            [l['btn_nx'], l['btn_orig']],
            [l['btn_pro'], l['btn_settings']]
        ],
        resize_keyboard=True
    )

def get_discount_inline_kb():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("-5%", callback_data="d_5"), InlineKeyboardButton("-10%", callback_data="d_10"), InlineKeyboardButton("-15%", callback_data="d_15"), InlineKeyboardButton("-20%", callback_data="d_20")],
        [InlineKeyboardButton("-25%", callback_data="d_25"), InlineKeyboardButton("-30%", callback_data="d_30"), InlineKeyboardButton("-35%", callback_data="d_35"), InlineKeyboardButton("-40%", callback_data="d_40")],
        [InlineKeyboardButton("-50%", callback_data="d_50"), InlineKeyboardButton("-60%", callback_data="d_60"), InlineKeyboardButton("-70%", callback_data="d_70"), InlineKeyboardButton("-75%", callback_data="d_75")],
    ])

def get_lang_kb():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("Русский", callback_data="set_ru"), InlineKeyboardButton("Українська", callback_data="set_uk")]
    ])

def get_pro_inline_kb(lang_code):
    l = LOCALIZATION[lang_code]
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(l['pro_btn_auto'], callback_data="pro_auto")],
        [InlineKeyboardButton(l['pro_btn_fixed'], callback_data="pro_fixed")],
        [InlineKeyboardButton(l['pro_btn_loyal'], callback_data="pro_loyal")],
        [InlineKeyboardButton(l['pro_btn_double'], callback_data="pro_double")],
        [InlineKeyboardButton(l['pro_btn_compare'], callback_data="pro_compare")],
        [InlineKeyboardButton(l['pro_btn_margin'], callback_data="pro_margin")],
    ])

# --- ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ---

async def send_mode_message(update: Update, context: ContextTypes.DEFAULT_TYPE, mode_key: str):
    """Отправляет сообщение о смене режима и удаляет старое"""
    lang = get_lang(context)
    text = LOCALIZATION[lang][mode_key]
    
    # Удаляем старое сообщение с кнопками (если было)
    old_id = context.user_data.get('last_msg_id')
    if old_id:
        try:
            await context.bot.delete_message(chat_id=update.effective_chat.id, message_id=old_id)
        except Exception:
            pass
            
    # Отправляем новое
    msg = await update.message.reply_text(text, parse_mode='Markdown')
    context.user_data['last_msg_id'] = msg.message_id

# --- ОБРАБОТЧИКИ ПЕРЕКЛЮЧЕНИЯ РЕЖИМОВ (MENU HANDLER) ---

async def switch_mode(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    lang = get_lang(context)
    l = LOCALIZATION[lang]
    
    if text == l['btn_shelf']:
        await send_mode_message(update, context, 'mode_shelf_active')
        return MODE_SHELF
        
    elif text == l['btn_nx']:
        await send_mode_message(update, context, 'mode_nx_active')
        return MODE_NX
        
    elif text == l['btn_kg']:
        await send_mode_message(update, context, 'mode_kg_active')
        return MODE_KG
        
    elif text == l['btn_orig']:
        await send_mode_message(update, context, 'mode_orig_active')
        return MODE_ORIGINAL
    
    elif text == l['btn_pro']:
        # Для PRO режима отправляем инлайн клавиатуру
        await update.message.reply_text(l['pro_menu_text'], reply_markup=get_pro_inline_kb(lang))
        return MODE_PRO
        
    elif text == l['btn_settings']:
        await update.message.reply_text("🌐", reply_markup=get_lang_kb())
        return SETTINGS
        
    return None

# --- ЛОГИКА РЕЖИМОВ ---

async def handle_shelf(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Проверяем, не нажал ли юзер кнопку меню
    new_mode = await switch_mode(update, context)
    if new_mode is not None: return new_mode

    lang = get_lang(context)
    l = LOCALIZATION[lang]
    text = update.message.text.replace(',', '.')
    
    nums = [float(x) for x in re.findall(r'-?\d+(?:\.\d+)?', text)]
    
    if not nums:
        await update.message.reply_text(l['err_num'])
        return MODE_SHELF

    if len(nums) == 1:
        # Только цена -> показываем кнопки скидок
        price = nums[0]
        context.user_data['temp_price'] = price
        msg = await update.message.reply_text(
            l['ask_discount'].format(price=price),
            parse_mode='Markdown',
            reply_markup=get_discount_inline_kb()
        )
        context.user_data['last_msg_id'] = msg.message_id
        
    elif len(nums) >= 2:
        # Цена и скидка сразу
        price, disc = nums[0], nums[1]
        final = price * (1 - disc/100)
        diff = price - final
        await update.message.reply_text(
            l['res_shelf'].format(price=price, disc=disc, total=f"{final:.2f}", diff=f"{diff:.2f}"),
            parse_mode='Markdown'
        )
    return MODE_SHELF

async def handle_nx(update: Update, context: ContextTypes.DEFAULT_TYPE):
    new_mode = await switch_mode(update, context)
    if new_mode is not None: return new_mode

    lang = get_lang(context)
    l = LOCALIZATION[lang]
    text = update.message.text.replace(',', '.')
    nums = [float(x) for x in re.findall(r'-?\d+(?:\.\d+)?', text)]

    if len(nums) < 3:
        await update.message.reply_text(l['err_format'].format(hint="`2 1 50`"), parse_mode='Markdown')
        return MODE_NX
    
    n, x, price = int(nums[0]), int(nums[1]), nums[2]
    count = n + x
    total_pay = price * n
    unit_price = total_pay / count
    real_disc = (x / count) * 100
    
    await update.message.reply_text(
        l['res_nx'].format(n=n, x=x, count=count, total_pay=total_pay, unit=unit_price, real_disc=real_disc),
        parse_mode='Markdown'
    )
    return MODE_NX

async def handle_kg(update: Update, context: ContextTypes.DEFAULT_TYPE):
    new_mode = await switch_mode(update, context)
    if new_mode is not None: return new_mode
    
    lang = get_lang(context)
    l = LOCALIZATION[lang]
    text = update.message.text.replace(',', '.')
    nums = [float(x) for x in re.findall(r'-?\d+(?:\.\d+)?', text)]

    if len(nums) < 2:
        await update.message.reply_text(l['err_format'].format(hint="`130 400`"), parse_mode='Markdown')
        return MODE_KG

    price, weight = nums[0], nums[1]
    kg_price = (price / weight) * 1000
    g100 = (price / weight) * 100
    
    await update.message.reply_text(
        l['res_kg'].format(weight=weight, price=price, kg_price=f"{kg_price:.2f}", g100=f"{g100:.2f}"),
        parse_mode='Markdown'
    )
    return MODE_KG

async def handle_original(update: Update, context: ContextTypes.DEFAULT_TYPE):
    new_mode = await switch_mode(update, context)
    if new_mode is not None: return new_mode

    lang = get_lang(context)
    l = LOCALIZATION[lang]
    text = update.message.text.replace(',', '.')
    nums = [float(x) for x in re.findall(r'-?\d+(?:\.\d+)?', text)]

    if len(nums) < 2:
        await update.message.reply_text(l['err_format'].format(hint="`199 20`"), parse_mode='Markdown')
        return MODE_ORIGINAL

    final, disc = nums[0], nums[1]
    orig = final / (1 - disc/100)
    
    await update.message.reply_text(
        l['res_orig'].format(final=final, disc=disc, orig=f"{orig:.2f}"),
        parse_mode='Markdown'
    )
    return MODE_ORIGINAL

# --- PRO ИНСТРУМЕНТЫ (Упрощенные для примера) ---
# Для полного PRO функционала можно расширять этот блок

async def handle_pro_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Если ввели текст в меню PRO, проверяем, может это смена режима
    new_mode = await switch_mode(update, context)
    if new_mode is not None: return new_mode
    return MODE_PRO

async def pro_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    
    if data == "pro_auto":
        await query.message.reply_text("🤖 Введите выражение (например `2+1 50` или `300-20%`):")
        context.user_data['pro_func'] = 'auto'
        return MODE_PRO_INPUT
    # Здесь можно добавить обработку других кнопок
    
    await query.message.reply_text("🚧 Эта функция в разработке")
    return MODE_PRO

async def handle_pro_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    new_mode = await switch_mode(update, context)
    if new_mode is not None: return new_mode
    
    # Тут логика обработки данных для PRO
    text = update.message.text
    # Простейший авто-детект (из прошлого кода)
    if "auto" in context.user_data.get('pro_func', ''):
        # ... (сюда можно вставить логику парсинга из прошлого файла)
        await update.message.reply_text(f"Вы ввели: {text}. (Логика PRO)")
    
    return MODE_PRO_INPUT

# --- ОБЩИЕ ОБРАБОТЧИКИ ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = get_lang(context)
    context.user_data['lang'] = lang
    await update.message.reply_text(
        LOCALIZATION[lang]['welcome'],
        reply_markup=get_main_keyboard(lang),
        parse_mode='Markdown'
    )
    return MODE_SHELF

async def inline_discount(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    lang = get_lang(context)
    l = LOCALIZATION[lang]
    
    disc = float(query.data.split('_')[1])
    price = context.user_data.get('temp_price')
    
    if not price:
        await query.message.edit_text("⚠️ Цена устарела.")
        return
        
    final = price * (1 - disc/100)
    diff = price - final
    await query.message.edit_text(
        l['res_shelf'].format(price=price, disc=disc, total=f"{final:.2f}", diff=f"{diff:.2f}"),
        parse_mode='Markdown'
    )

async def set_language(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    lang = query.data.split('_')[1]
    context.user_data['lang'] = lang
    
    await query.message.delete()
    await query.message.reply_text(
        LOCALIZATION[lang]['saved'],
        reply_markup=get_main_keyboard(lang)
    )
    return MODE_SHELF

# ===== ЗАПУСК =====

def get_application():
    if not TOKEN:
        raise ValueError("Токен не найден! Проверь переменные окружения.")
    
    app = ApplicationBuilder().token(TOKEN).build()
    
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            MODE_SHELF: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_shelf)],
            MODE_NX: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_nx)],
            MODE_KG: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_kg)],
            MODE_ORIGINAL: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_original)],
            MODE_PRO: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_pro_menu),
                CallbackQueryHandler(pro_callback, pattern="^pro_")
            ],
            MODE_PRO_INPUT: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_pro_input)],
            SETTINGS: [CallbackQueryHandler(set_language, pattern="^set_")]
        },
        fallbacks=[CommandHandler("start", start)],
        per_chat=True
    )
    
    app.add_handler(conv_handler)
    app.add_handler(CallbackQueryHandler(inline_discount, pattern="^d_")) # Обработка скидок работает везде
    
    return app
