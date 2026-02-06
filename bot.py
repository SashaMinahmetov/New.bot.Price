import os
import logging
import asyncio
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

# Состояния диалога
(
    ВЫБОР_ЯЗЫКА,
    ВЫБОР_ТИПА_СКИДКИ,
    ОЖИДАНИЕ_СВОЕЙ_СКИДКИ,
    ОЖИДАНИЕ_ЦЕНЫ,
    ОЖИДАНИЕ_N,
    ОЖИДАНИЕ_X,
    ОЖИДАНИЕ_ЦЕНЫ_NX,
    ОЖИДАНИЕ_ЦЕНЫ_ВЕС,
    ОЖИДАНИЕ_ГРАММОВ,
    ОЖИДАНИЕ_ЦЕНЫ_СО_СКИДКОЙ,
    ОЖИДАНИЕ_ПРОЦЕНТА_СКИДКИ,
    ОЖИДАНИЕ_ЗАКУПКИ,      # Для маржи
    ОЖИДАНИЕ_ПОЛКИ_МАРЖА,  # Для маржи
    НАСТРОЙКИ,
) = range(14)

# Настройка логирования
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Словари с локализацией
LOCALIZATION = {
    'ru': {
        'welcome': "👋 Добро пожаловать! Выберите язык:",
        'main_menu': "👋 Добро пожаловать! Выберите опцию:",
        'select_discount': "📦 Выберите процент скидки:",
        'enter_custom_discount': "🎯 Введите процент скидки (например, 15 или 14.5):",
        'enter_price': "🔢 Введите цену на полке (например, 545.00):",
        'price_result': "{title}\n\n💰 Цена на полке: {price:.2f} грн\n⬇️ Скидка: {discount}%{extra}\n✅ ИТОГО: {discounted_price:.2f}",
        'invalid_discount': "❌ Ошибка. Скидка должна быть от 0% до 100%.",
        'invalid_price': "❌ Ошибка. Введите цену числом, например: 545.44.",
        'enter_n': "🔢 Введите количество товаров к покупке (N):",
        'enter_x': "🎁 Введите количество товаров в подарок (X):",
        'enter_nx_price': "💰 Введите цену одного товара:",
        'nx_result': "{title}\n\n🛒 Акция: {n}+{x}\n💰 Цена товара: {price:.2f} грн\n🏁 Всего за набор: {total:.2f} грн\n📉 Реальная скидка: {discount:.2f}%\n✅ Цена за шт. в наборе: {unit_price:.2f}",
        'enter_weight_price': "💰 Введите цену упаковки:",
        'enter_weight': "⚖️ Введите вес/объем (грамм или мл):",
        'weight_result': '{title}\n\n📦 Упаковка: {weight:.2f} г/мл\n💰 Цена: {price:.2f} грн\n\n✅ Цена за 1 кг/л: {kg_price:.2f} грн\n📏 Цена за 100 г/мл: {price_100g:.2f}',
        'enter_price_short': 'Введите цену товара:',
        'enter_weight_short': 'Введите вес (г) или объем (мл):',
        'invalid_number': 'Пожалуйста, введите корректное число больше 0.',
        'error': '❌ Ошибка. Введите /start для перезапуска.',
        'cancel': "❌ Отменено. Введите /start.",
        'restart': "🔄 Бот перезапущен!",
        'unexpected_text': "❌ Используйте кнопки меню.",
        'settings_menu': "⚙️ Настройки:",
        'change_language': "🔄 Сменить язык",
        'clear_chat_btn': "🗑 Очистить чат",
        'chat_cleared': "✅ История сообщений бота очищена!",
        'back': "🔙 Назад",
        'back_to_menu_btn': "🏠 В главное меню",
        'next_action_prompt': "📊 Что считаем дальше?",
        'restart_btn': "🔄 Перезапустить бота",
        'btn_show_calc': "📝 Показать расчёт",
        'btn_hide_calc': "🙈 Скрыть расчёт",
        
        # Шаблоны объяснений
        'expl_header': "\n\n📝 <b>Подробный расчёт:</b>\n",
        'expl_shelf': "Цена - (Цена × Скидка / 100)\n{price} - ({price} × {discount} / 100) = <b>{result:.2f}</b>",
        'expl_nx': "1. Всего товаров: {n} + {x} = {total_qty}\n2. Платим только за {n}: {price} × {n} = {total_sum:.2f}\n3. Цена за шт: {total_sum:.2f} / {total_qty} = <b>{unit_price:.2f}</b>",
        'expl_weight': "Цена / Вес × 1000\n({price} / {weight}) × 1000 = <b>{kg_price:.2f}</b> за кг",
        'expl_original': "Цена со скидкой / (1 - Скидка / 100)\n{price} / (1 - {discount} / 100) = <b>{result:.2f}</b>",
        'expl_margin': "• Прибыль = Полка - Закупка\n  {shelf} - {cost} = {profit:.2f}\n\n• Наценка = (Прибыль / Закупка) × 100\n  ({profit:.2f} / {cost}) × 100 = <b>{markup:.1f}%</b>\n\n• Маржа = (Прибыль / Полка) × 100\n  ({profit:.2f} / {shelf}) × 100 = <b>{margin:.1f}%</b>",

        'mode_shelf': "🏷 Расчет цены со скидкой",
        'mode_nx': "🎁 Расчет акции N+X",
        'mode_per_kg': "⚖️ Расчет цены за кг/л",
        'mode_original_price': "🔙 Поиск исходной цены",
        'mode_margin': "📊 Расчет маржи и наценки",
        
        'calc_title_shelf': "🏷 Цена со скидкой",
        'calc_title_nx': "🎁 Акция N+X",
        'calc_title_per_kg': "⚖️ Цена за кг/л",
        'calc_title_original_price': "🔙 Цена без скидки",
        
        'main_menu_btn': [
            ("🏷 Цена со скидкой", "menu_shelf_discount"),
            ("🎁 Акция N+X", "menu_nx"), 
            ("⚖️ Цена за кг/л", "menu_per_kg"),
            ("🔙 Цена без скидки", "menu_original_price"),
            ("📊 Маржа и Наценка", "menu_margin"),
            ("⚙️ Настройки", "настройки"),
        ],
        'discount_buttons': [
            [("5%", "5"), ("10%", "10"), ("15%", "15"), ("20%", "20")],
            [("25%", "25"), ("30%", "30"), ("35%", "35"), ("40%", "40")],
            [("45%", "45"), ("50%", "50"), ("Другая %", "другая_скидка")]
        ],
        'margin_enter_cost': "💼 Введите закупочную цену:",
        'margin_enter_shelf': "🏷️ Введите цену на полке:",
    },
    'uk': {
        'welcome': "👋 Ласкаво просимо! Оберіть мову:",
        'main_menu': "👋 Ласкаво просимо! Оберіть опцію:",
        'select_discount': "📦 Оберіть відсоток знижки:",
        'enter_custom_discount': "🎯 Введіть свій відсоток знижки (наприклад, 15 або 14.5):",
        'enter_price': "🔢 Введіть ціну на полиці (наприклад, 545.00):",
        'price_result': "{title}\n\n💰 Ціна на полиці: {price:.2f} грн\n⬇️ Знижка: {discount}%{extra}\n✅ РАЗОМ: {discounted_price:.2f}",
        'invalid_discount': "❌ Помилка. Знижка має бути від 0% до 100%.",
        'invalid_price': "❌ Помилка. Введіть ціну числом, наприклад: 545.44.",
        'enter_n': "🔢 Введіть кількість товарів до покупки (N):",
        'enter_x': "🎁 Введіть кількість товарів у подарунок (X):",
        'enter_nx_price': "💰 Введіть ціну одного товару:",
        'nx_result': "{title}\n\n🛒 Акція: {n}+{x}\n💰 Ціна одного товару: {price:.2f}\n🏁 Всього за набір: {total:.2f}\n📉 Реальна знижка: {discount:.2f}%\n✅ Ціна за шт. в наборі: {unit_price:.2f}",
        'enter_weight_price': "💰 Введіть ціну упаковки:",
        'enter_weight': "⚖️ Введіть вагу/об'єм (грамів або мл):",
        'weight_result': '{title}\n\n📦 Упаковка: {weight:.2f} г/мл\n💰 Ціна: {price:.2f}\n\n✅ Ціна за 1 кг/л: {kg_price:.2f}\n📏 Ціна за 100 г/мл: {price_100g:.2f}',
        'enter_price_short': 'Введіть ціну товару:',
        'enter_weight_short': 'Введіть вагу (г) або об\'єм (мл):',
        'invalid_number': 'Будь ласка, введіть коректне число більше 0.',
        'error': '❌ Помилка. Введіть /start для перезапуску.',
        'cancel': "❌ Скасовано. Введіть /start.",
        'restart': "🔄 Бот перезапущено!",
        'unexpected_text': "❌ Використовуйте кнопки меню.",
        'settings_menu': "⚙️ Налаштування:",
        'change_language': "🔄 Змінити мову",
        'clear_chat_btn': "🗑 Очистити чат",
        'chat_cleared': "✅ Історія повідомлень бота очищена!",
        'back': "🔙 Назад",
        'back_to_menu_btn': "🏠 В головне меню",
        'next_action_prompt': "📊 Що рахуємо далі?",
        'restart_btn': "🔄 Перезапустити бота",
        'btn_show_calc': "📝 Показати розрахунок",
        'btn_hide_calc': "🙈 Приховати розрахунок",

        'expl_header': "\n\n📝 <b>Детальний розрахунок:</b>\n",
        'expl_shelf': "Ціна - (Ціна × Знижка / 100)\n{price} - ({price} × {discount} / 100) = <b>{result:.2f}</b>",
        'expl_nx': "1. Всього товарів: {n} + {x} = {total_qty}\n2. Платимо тільки за {n}: {price} × {n} = {total_sum:.2f}\n3. Ціна за шт: {total_sum:.2f} / {total_qty} = <b>{unit_price:.2f}</b>",
        'expl_weight': "Ціна / Вага × 1000\n({price} / {weight}) × 1000 = <b>{kg_price:.2f}</b> за кг",
        'expl_original': "Ціна зі знижкою / (1 - Знижка / 100)\n{price} / (1 - {discount} / 100) = <b>{result:.2f}</b>",
        'expl_margin': "• Прибуток = Полиця - Закупівля\n  {shelf} - {cost} = {profit:.2f}\n\n• Націнка = (Прибуток / Закупівля) × 100\n  ({profit:.2f} / {cost}) × 100 = <b>{markup:.1f}%</b>\n\n• Маржа = (Прибуток / Полиця) × 100\n  ({profit:.2f} / {shelf}) × 100 = <b>{margin:.1f}%</b>",

        'mode_shelf': "🏷 Розрахунок ціни зі знижкою",
        'mode_nx': "🎁 Розрахунок акції N+X",
        'mode_per_kg': "⚖️ Розрахунок ціни за кг/л",
        'mode_original_price': "🔙 Пошук вихідної ціни",
        'mode_margin': "📊 Розрахунок маржі та націнки",
        
        'calc_title_shelf': "🏷 Ціна зі знижкою",
        'calc_title_nx': "🎁 Акція N+X",
        'calc_title_per_kg': "⚖️ Ціна за кг/л",
        'calc_title_original_price': "🔙 Ціна без знижки",
        
        'main_menu_btn': [
            ("🏷 Ціна зі знижкою", "menu_shelf_discount"),
            ("🎁 Акція N+X", "menu_nx"),
            ("⚖️ Ціна за кг/л", "menu_per_kg"),
            ("🔙 Ціна без знижки", "menu_original_price"),
            ("📊 Маржа та Націнка", "menu_margin"),
            ("⚙️ Налаштування", "настройки"),
        ],
        'discount_buttons': [
            [("5%", "5"), ("10%", "10"), ("15%", "15"), ("20%", "20")],
            [("25%", "25"), ("30%", "30"), ("35%", "35"), ("40%", "40")],
            [("45%", "45"), ("50%", "50"), ("Інший %", "інша_знижка")]
        ],
        'margin_enter_cost': "💼 Введіть закупівельну ціну:",
        'margin_enter_shelf': "🏷️ Введіть ціну на полиці:",
    },
    'en': {
        'welcome': "👋 Welcome! Choose your language:",
        'main_menu': "👋 Welcome! Choose an option:",
        'select_discount': "📦 Select discount percentage:",
        'enter_custom_discount': "🎯 Enter custom discount (e.g., 15 or 14.5):",
        'enter_price': "🔢 Enter shelf price (e.g., 545.00):",
        'price_result': "{title}\n\n💰 Shelf Price: {price:.2f}\n⬇️ Discount: {discount}%{extra}\n✅ TOTAL: {discounted_price:.2f}",
        'invalid_discount': "❌ Error. Discount must be between 0% and 100%.",
        'invalid_price': "❌ Error. Please enter a valid number, e.g., 545.44.",
        'enter_n': "🔢 Enter quantity to buy (N):",
        'enter_x': "🎁 Enter free quantity (X):",
        'enter_nx_price': "💰 Enter price per item:",
        'nx_result': "{title}\n\n🛒 Promo: {n}+{x}\n💰 Item Price: {price:.2f}\n🏁 Total Sum: {total:.2f}\n📉 Real Discount: {discount:.2f}%\n✅ Unit Price: {unit_price:.2f}",
        'enter_weight_price': "💰 Enter pack price:",
        'enter_weight': "⚖️ Enter weight/volume (grams or ml):",
        'weight_result': '{title}\n\n📦 Pack: {weight:.2f} g/ml\n💰 Price: {price:.2f}\n\n✅ Price per 1 kg/l: {kg_price:.2f}\n📏 Price per 100 g/ml: {price_100g:.2f}',
        'enter_price_short': 'Enter item price:',
        'enter_weight_short': 'Enter weight (g) or volume (ml):',
        'invalid_number': 'Please enter a valid number greater than 0.',
        'error': '❌ Error. Type /start to restart.',
        'cancel': "❌ Canceled. Type /start.",
        'restart': "🔄 Bot restarted!",
        'unexpected_text': "❌ Please use menu buttons.",
        'settings_menu': "⚙️ Settings:",
        'change_language': "🔄 Change Language",
        'clear_chat_btn': "🗑 Clear Chat",
        'chat_cleared': "✅ Bot message history cleared!",
        'back': "🔙 Back",
        'back_to_menu_btn': "🏠 Main Menu",
        'next_action_prompt': "📊 What's next?",
        'restart_btn': "🔄 Restart Bot",
        'btn_show_calc': "📝 Show Calculation",
        'btn_hide_calc': "🙈 Hide Calculation",
        
        'expl_header': "\n\n📝 <b>Calculation Details:</b>\n",
        'expl_shelf': "Price - (Price × Discount / 100)\n{price} - ({price} × {discount} / 100) = <b>{result:.2f}</b>",
        'expl_nx': "1. Total items: {n} + {x} = {total_qty}\n2. Pay only for {n}: {price} × {n} = {total_sum:.2f}\n3. Unit price: {total_sum:.2f} / {total_qty} = <b>{unit_price:.2f}</b>",
        'expl_weight': "Price / Weight × 1000\n({price} / {weight}) × 1000 = <b>{kg_price:.2f}</b> per kg",
        'expl_original': "Discounted Price / (1 - Discount / 100)\n{price} / (1 - {discount} / 100) = <b>{result:.2f}</b>",
        'expl_margin': "• Profit = Shelf - Cost\n  {shelf} - {cost} = {profit:.2f}\n\n• Markup = (Profit / Cost) × 100\n  ({profit:.2f} / {cost}) × 100 = <b>{markup:.1f}%</b>\n\n• Margin = (Profit / Shelf) × 100\n  ({profit:.2f} / {shelf}) × 100 = <b>{margin:.1f}%</b>",

        'mode_shelf': "🏷 Discount Calculator",
        'mode_nx': "🎁 N+X Promo Calculator",
        'mode_per_kg': "⚖️ Price per kg/l Calculator",
        'mode_original_price': "🔙 Reverse Price Calculator",
        'mode_margin': "📊 Margin & Markup Calculator",
        
        'calc_title_shelf': "🏷 Discount Price",
        'calc_title_nx': "🎁 N+X Promo",
        'calc_title_per_kg': "⚖️ Price per kg/l",
        'calc_title_original_price': "🔙 Original Price",
        
        'main_menu_btn': [
            ("🏷 Discount Price", "menu_shelf_discount"),
            ("🎁 Promo N+X", "menu_nx"),
            ("⚖️ Price per kg/l", "menu_per_kg"),
            ("🔙 Original Price", "menu_original_price"),
            ("📊 Margin & Markup", "menu_margin"),
            ("⚙️ Settings", "настройки"),
        ],
        'discount_buttons': [
            [("5%", "5"), ("10%", "10"), ("15%", "15"), ("20%", "20")],
            [("25%", "25"), ("30%", "30"), ("35%", "35"), ("40%", "40")],
            [("45%", "45"), ("50%", "50"), ("Other %", "другая_скидка")]
        ],
        'margin_enter_cost': "💼 Enter cost price:",
        'margin_enter_shelf': "🏷️ Enter shelf price:",
    }
}

# ===== ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ =====

def get_language(context: ContextTypes.DEFAULT_TYPE | None) -> str:
    try:
        if context is not None and getattr(context, "user_data", None) is not None:
            return context.user_data.get('language', 'ru')
    except Exception:
        pass
    return 'ru'

def add_to_history(context: ContextTypes.DEFAULT_TYPE, entry: str) -> None:
    history = context.user_data.get("history", [])
    history.append(entry)
    if len(history) > 10:
        history = history[-10:]
    context.user_data["history"] = history

async def send_clean_message(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    text: str,
    reply_markup=None,
    keep_result: bool = False,
    parse_mode: str = None
):
    bot = context.bot
    if update.callback_query:
        chat = update.callback_query.message.chat
        trigger_message_id = update.callback_query.message.message_id
    else:
        chat = update.message.chat
        trigger_message_id = update.message.message_id

    old_ids = context.user_data.get("messages_to_delete", [])
    for mid in old_ids:
        try:
            await bot.delete_message(chat_id=chat.id, message_id=mid)
        except Exception:
            pass
    context.user_data["messages_to_delete"] = []

    try:
        await bot.delete_message(chat.id, trigger_message_id)
    except Exception:
        pass

    sent = await bot.send_message(chat_id=chat.id, text=text, reply_markup=reply_markup, parse_mode=parse_mode)

    all_bot = context.user_data.get("all_bot_messages", [])
    all_bot.append(sent.message_id)
    context.user_data["all_bot_messages"] = all_bot

    if not keep_result:
        context.user_data["messages_to_delete"].append(sent.message_id)

    return sent

async def delete_mode_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    mode_id = context.user_data.pop('mode_message_id', None)
    if not mode_id:
        return
    chat = update.effective_chat
    if not chat:
        return
    try:
        await context.bot.delete_message(chat_id=chat.id, message_id=mode_id)
    except Exception:
        pass

def get_language_keyboard():
    keyboard = [
        [InlineKeyboardButton("Русский", callback_data="lang_ru"), InlineKeyboardButton("Українська", callback_data="lang_uk")],
        [InlineKeyboardButton("English", callback_data="lang_en")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_main_menu_keyboard(context: ContextTypes.DEFAULT_TYPE):
    lang = get_language(context)
    keyboard = [
        [InlineKeyboardButton(text, callback_data=data)]
        for text, data in LOCALIZATION[lang]['main_menu_btn']
    ]
    return InlineKeyboardMarkup(keyboard)

def get_next_actions_keyboard(context: ContextTypes.DEFAULT_TYPE):
    lang = get_language(context)
    keyboard = [
        [InlineKeyboardButton(text, callback_data=data)]
        for text, data in LOCALIZATION[lang]['main_menu_btn']
    ]
    keyboard.append([
        InlineKeyboardButton(
            LOCALIZATION[lang]['restart_btn'],
            callback_data="перезапустить_бот"
        )
    ])
    return InlineKeyboardMarkup(keyboard)

def get_discount_keyboard(context: ContextTypes.DEFAULT_TYPE):
    lang = get_language(context)
    keyboard = [
        [InlineKeyboardButton(text, callback_data=data) for text, data in row]
        for row in LOCALIZATION[lang]['discount_buttons']
    ]
    keyboard.append([InlineKeyboardButton(LOCALIZATION[lang]['back_to_menu_btn'], callback_data="to_menu")])
    return InlineKeyboardMarkup(keyboard)

def get_settings_keyboard(context: ContextTypes.DEFAULT_TYPE):
    lang = get_language(context)
    keyboard = [
        [InlineKeyboardButton(LOCALIZATION[lang]['change_language'], callback_data="сменить_язык")],
        [InlineKeyboardButton(LOCALIZATION[lang]['clear_chat_btn'], callback_data="clear_chat")],
        [InlineKeyboardButton(LOCALIZATION[lang]['back_to_menu_btn'], callback_data="to_menu")],
    ]
    return InlineKeyboardMarkup(keyboard)

def get_back_keyboard(context: ContextTypes.DEFAULT_TYPE):
    lang = get_language(context)
    keyboard = [
        [InlineKeyboardButton(LOCALIZATION[lang]['back'], callback_data="назад")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_back_to_menu_keyboard(context: ContextTypes.DEFAULT_TYPE):
    lang = get_language(context)
    keyboard = [
        [InlineKeyboardButton(LOCALIZATION[lang]['back_to_menu_btn'], callback_data="to_menu")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_result_keyboard(context: ContextTypes.DEFAULT_TYPE):
    """Клавиатура с кнопкой ПОКАЗАТЬ РАСЧЕТ"""
    lang = get_language(context)
    keyboard = [
        [InlineKeyboardButton(LOCALIZATION[lang]['btn_show_calc'], callback_data="show_calc")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_hide_result_keyboard(context: ContextTypes.DEFAULT_TYPE):
    """Клавиатура с кнопкой СКРЫТЬ РАСЧЕТ"""
    lang = get_language(context)
    keyboard = [
        [InlineKeyboardButton(LOCALIZATION[lang]['btn_hide_calc'], callback_data="hide_calc")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_numeric_reply_keyboard():
    keyboard = [
        ["1", "2", "3"],
        ["4", "5", "6"],
        ["7", "8", "9"],
        ["10"],
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)

# ===== ОБРАБОТЧИКИ =====

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if 'mode_message_id' in context.user_data:
        await delete_mode_message(update, context)

    if 'language' not in context.user_data:
        context.user_data['попередній_стан'] = ВЫБОР_ЯЗЫКА
        await send_clean_message(
            update,
            context,
            "👋 Выберите язык / Оберіть мову / Choose language:",
            reply_markup=get_language_keyboard()
        )
        return ВЫБОР_ЯЗЫКА

    lang = get_language(context)
    saved_lang = lang
    context.user_data.clear()
    context.user_data['language'] = saved_lang
    context.user_data['попередній_стан'] = ВЫБОР_ТИПА_СКИДКИ
    keyboard = get_main_menu_keyboard(context)

    await send_clean_message(
        update,
        context,
        LOCALIZATION[lang]['main_menu'],
        reply_markup=keyboard
    )
    return ВЫБОР_ТИПА_СКИДКИ

async def choose_language(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    lang = query.data.split('_')[1]
    context.user_data['language'] = lang
    context.user_data['попередній_стан'] = ВЫБОР_ТИПА_СКИДКИ
    keyboard = get_main_menu_keyboard(context)

    await send_clean_message(
        update,
        context,
        LOCALIZATION[lang]['main_menu'],
        reply_markup=keyboard
    )
    return ВЫБОР_ТИПА_СКИДКИ

async def settings_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    lang = get_language(context)
    context.user_data['попередній_стан'] = ВЫБОР_ТИПА_СКИДКИ
    await update.callback_query.answer()

    await send_clean_message(
        update,
        context,
        LOCALIZATION[lang]['settings_menu'],
        reply_markup=get_settings_keyboard(context)
    )
    return НАСТРОЙКИ

async def change_language(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.callback_query.answer()
    context.user_data['попередній_стан'] = НАСТРОЙКИ
    await send_clean_message(
        update,
        context,
        "👋 Выберите язык / Оберіть мову / Choose language:",
        reply_markup=get_language_keyboard()
    )
    return ВЫБОР_ЯЗЫКА

async def clear_chat_history(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.callback_query.answer()
    
    bot_messages = context.user_data.get("all_bot_messages", [])
    chat_id = update.effective_chat.id
    
    for msg_id in bot_messages:
        try:
            await context.bot.delete_message(chat_id=chat_id, message_id=msg_id)
        except Exception:
            pass
            
    context.user_data["all_bot_messages"] = []
    
    lang = get_language(context)
    await context.bot.send_message(
        chat_id=chat_id, 
        text=LOCALIZATION[lang]['chat_cleared']
    )
    
    # Возвращаем пользователя в главное меню
    return await start(update, context)

# --- ОСНОВНЫЕ ФУНКЦИИ ---

async def calculate_shelf_discount(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    lang = get_language(context)
    context.user_data['текущее_действие'] = 'menu_shelf_discount'
    context.user_data['попередній_стан'] = ВЫБОР_ТИПА_СКИДКИ 
    
    if update.callback_query:
        await update.callback_query.answer()

    mode_msg = await send_clean_message(
        update,
        context,
        LOCALIZATION[lang]['mode_shelf'],
        reply_markup=None,
        keep_result=True,
    )
    context.user_data['mode_message_id'] = mode_msg.message_id

    await send_clean_message(
        update,
        context,
        LOCALIZATION[lang]['select_discount'],
        reply_markup=get_discount_keyboard(context)
    )
    return ВЫБОР_ТИПА_СКИДКИ

async def handle_fixed_discount(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    lang = get_language(context)
    await update.callback_query.answer()
    discount = float(update.callback_query.data)
    context.user_data['скидка'] = discount
    context.user_data['попередній_стан'] = ВЫБОР_ТИПА_СКИДКИ 

    await send_clean_message(
        update,
        context,
        LOCALIZATION[lang]['enter_price'],
        reply_markup=get_back_keyboard(context)
    )
    return ОЖИДАНИЕ_ЦЕНЫ

async def custom_discount(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    lang = get_language(context)
    context.user_data['попередній_стан'] = ВЫБОР_ТИПА_СКИДКИ
    await update.callback_query.answer()

    await send_clean_message(
        update,
        context,
        LOCALIZATION[lang]['enter_custom_discount'],
        reply_markup=get_back_keyboard(context)
    )
    return ОЖИДАНИЕ_СВОЕЙ_СКИДКИ

async def handle_discount_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    lang = get_language(context)
    try:
        text = update.message.text.replace(',', '.')
        if not all(c.isdigit() or c == '.' for c in text):
            await send_clean_message(update, context, LOCALIZATION[lang]['invalid_discount'], reply_markup=get_back_keyboard(context))
            return ОЖИДАНИЕ_СВОЕЙ_СКИДКИ

        discount = float(text)
        if discount <= 0 or discount >= 100:
            await send_clean_message(update, context, LOCALIZATION[lang]['invalid_discount'], reply_markup=get_back_keyboard(context))
            return ОЖИДАНИЕ_СВОЕЙ_СКИДКИ

        context.user_data['скидка'] = discount
        context.user_data['попередній_стан'] = ОЖИДАНИЕ_СВОЕЙ_СКИДКИ

        await send_clean_message(
            update,
            context,
            LOCALIZATION[lang]['enter_price'],
            reply_markup=get_back_keyboard(context)
        )
        return ОЖИДАНИЕ_ЦЕНЫ
    except ValueError:
        await send_clean_message(update, context, LOCALIZATION[lang]['invalid_discount'], reply_markup=get_back_keyboard(context))
        return ОЖИДАНИЕ_СВОЕЙ_СКИДКИ
    except Exception as e:
        logger.error(f"Error: {e}")
        await send_clean_message(update, context, LOCALIZATION[lang]['error'], reply_markup=get_back_keyboard(context))
        return ОЖИДАНИЕ_СВОЕЙ_СКИДКИ

async def handle_price_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    lang = get_language(context)
    try:
        text = update.message.text.replace(',', '.')
        if not all(c.isdigit() or c == '.' for c in text):
            await send_clean_message(update, context, LOCALIZATION[lang]['invalid_price'], reply_markup=get_back_keyboard(context))
            return ОЖИДАНИЕ_ЦЕНЫ

        price = float(text)
        if price <= 0:
            await send_clean_message(update, context, LOCALIZATION[lang]['invalid_price'], reply_markup=get_back_keyboard(context))
            return ОЖИДАНИЕ_ЦЕНЫ

        discount = context.user_data.get('скидка', 0)
        discounted_price = price * (1 - discount / 100)
        extra = f" ({context.user_data.get('extra_discount_info', '')})" if context.user_data.get('extra_discount_info') else ""

        await delete_mode_message(update, context)
        title = LOCALIZATION[lang]['calc_title_shelf']

        result_text = LOCALIZATION[lang]['price_result'].format(
            title=title,
            price=price,
            discount=discount,
            extra=extra,
            discounted_price=discounted_price
        )
        
        explanation = LOCALIZATION[lang]['expl_shelf'].format(
            price=price,
            discount=discount,
            result=discounted_price
        )
        context.user_data['last_explanation'] = explanation
        
        await send_clean_message(
            update,
            context,
            result_text,
            reply_markup=get_result_keyboard(context), 
            keep_result=True,
        )
        add_to_history(context, result_text)

        await send_clean_message(
            update,
            context,
            LOCALIZATION[lang]['next_action_prompt'],
            reply_markup=get_next_actions_keyboard(context),
        )
        return ВЫБОР_ТИПА_СКИДКИ
    except ValueError:
        await send_clean_message(update, context, LOCALIZATION[lang]['invalid_price'], reply_markup=get_back_keyboard(context))
        return ОЖИДАНИЕ_ЦЕНЫ
    except Exception as e:
        logger.error(f"Error: {e}")
        await send_clean_message(update, context, LOCALIZATION[lang]['error'])
        return ОЖИДАНИЕ_ЦЕНЫ

# --- N+X ---

async def calculate_n_plus_x(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    lang = get_language(context)
    context.user_data['текущее_действие'] = 'menu_nx'
    context.user_data['попередній_стан'] = ВЫБОР_ТИПА_СКИДКИ
    context.user_data.pop('n', None)
    context.user_data.pop('x', None)

    if update.callback_query:
        await update.callback_query.answer()

    mode_msg = await send_clean_message(
        update,
        context,
        LOCALIZATION[lang]['mode_nx'],
        reply_markup=None,
        keep_result=True,
    )
    context.user_data['mode_message_id'] = mode_msg.message_id

    await send_clean_message(
        update,
        context,
        LOCALIZATION[lang]['enter_n'],
        reply_markup=get_back_to_menu_keyboard(context) 
    )
    return ОЖИДАНИЕ_N

async def handle_n_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    lang = get_language(context)
    text = update.message.text.strip()
    if not text.isdigit():
        await send_clean_message(update, context, LOCALIZATION[lang]['invalid_number'], reply_markup=get_back_to_menu_keyboard(context))
        return ОЖИДАНИЕ_N
    n = int(text)
    if n <= 0:
        await send_clean_message(update, context, LOCALIZATION[lang]['invalid_number'], reply_markup=get_back_to_menu_keyboard(context))
        return ОЖИДАНИЕ_N
    context.user_data['n'] = n
    context.user_data['попередній_стан'] = ОЖИДАНИЕ_N
    await send_clean_message(update, context, LOCALIZATION[lang]['enter_x'], reply_markup=get_back_keyboard(context))
    return ОЖИДАНИЕ_X

async def handle_x_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    lang = get_language(context)
    text = update.message.text.strip()
    if not text.isdigit():
        await send_clean_message(update, context, LOCALIZATION[lang]['invalid_number'], reply_markup=get_back_keyboard(context))
        return ОЖИДАНИЕ_X
    x = int(text)
    if x <= 0:
        await send_clean_message(update, context, LOCALIZATION[lang]['invalid_number'], reply_markup=get_back_keyboard(context))
        return ОЖИДАНИЕ_X
    context.user_data['x'] = x
    context.user_data['попередній_стан'] = ОЖИДАНИЕ_X
    await send_clean_message(update, context, LOCALIZATION[lang]['enter_nx_price'], reply_markup=get_back_keyboard(context))
    return ОЖИДАНИЕ_ЦЕНЫ_NX

async def handle_nx_price_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    lang = get_language(context)
    text = update.message.text.replace(',', '.')
    try:
        price = float(text)
        if price <= 0:
            await send_clean_message(update, context, LOCALIZATION[lang]['invalid_price'], reply_markup=get_back_keyboard(context))
            return ОЖИДАНИЕ_ЦЕНЫ_NX
        n = context.user_data.get('n')
        x = context.user_data.get('x')
        if n is None or x is None:
            await send_clean_message(update, context, LOCALIZATION[lang]['error'])
            return ВЫБОР_ТИПА_СКИДКИ
        total_quantity = n + x
        discount_percent = (x / total_quantity) * 100
        unit_price = price * n / total_quantity
        total_price = price * n
        await delete_mode_message(update, context)
        title = LOCALIZATION[lang]['calc_title_nx']
        result_text = LOCALIZATION[lang]['nx_result'].format(
            title=title, n=n, x=x, price=price, total=total_price, discount=discount_percent, unit_price=unit_price
        )
        
        explanation = LOCALIZATION[lang]['expl_nx'].format(
            n=n, x=x, total_qty=total_quantity, price=price, total_sum=total_price, unit_price=unit_price
        )
        context.user_data['last_explanation'] = explanation

        await send_clean_message(update, context, result_text, reply_markup=get_result_keyboard(context), keep_result=True)
        add_to_history(context, result_text)
        await send_clean_message(update, context, LOCALIZATION[lang]['next_action_prompt'], reply_markup=get_next_actions_keyboard(context))
        return ВЫБОР_ТИПА_СКИДКИ
    except ValueError:
        await send_clean_message(update, context, LOCALIZATION[lang]['invalid_price'], reply_markup=get_back_keyboard(context))
        return ОЖИДАНИЕ_ЦЕНЫ_NX
    except Exception:
        await send_clean_message(update, context, LOCALIZATION[lang]['error'])
        return ВЫБОР_ТИПА_СКИДКИ

# --- ЦЕНА ВЕСА ---

async def calculate_price_per_kg(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    lang = get_language(context)
    context.user_data['текущее_действие'] = 'menu_per_kg'
    context.user_data['попередній_стан'] = ВЫБОР_ТИПА_СКИДКИ
    context.user_data.pop('цена_веса', None)
    if update.callback_query:
        await update.callback_query.answer()
    mode_msg = await send_clean_message(update, context, LOCALIZATION[lang]['mode_per_kg'], reply_markup=None, keep_result=True)
    context.user_data['mode_message_id'] = mode_msg.message_id
    await send_clean_message(
        update, 
        context, 
        LOCALIZATION[lang]['enter_weight_price'], 
        reply_markup=get_back_to_menu_keyboard(context)
    )
    return ОЖИДАНИЕ_ЦЕНЫ_ВЕС

async def handle_weight_price_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    lang = get_language(context)
    text = update.message.text.replace(',', '.')
    try:
        price = float(text)
        if price <= 0:
            await send_clean_message(update, context, LOCALIZATION[lang]['invalid_price'], reply_markup=get_back_to_menu_keyboard(context))
            return ОЖИДАНИЕ_ЦЕНЫ_ВЕС
        context.user_data['цена_веса'] = price
        context.user_data['попередній_стан'] = ОЖИДАНИЕ_ЦЕНЫ_ВЕС
        await send_clean_message(update, context, LOCALIZATION[lang]['enter_weight'], reply_markup=get_back_keyboard(context))
        return ОЖИДАНИЕ_ГРАММОВ
    except ValueError:
        await send_clean_message(update, context, LOCALIZATION[lang]['invalid_price'], reply_markup=get_back_to_menu_keyboard(context))
        return ОЖИДАНИЕ_ЦЕНЫ_ВЕС

async def handle_weight_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    lang = get_language(context)
    text = update.message.text.replace(',', '.')
    try:
        weight = float(text)
        if weight <= 0:
            await send_clean_message(update, context, LOCALIZATION[lang]['invalid_number'], reply_markup=get_back_keyboard(context))
            return ОЖИДАНИЕ_ГРАММОВ
        price = context.user_data.get('цена_веса')
        if not price or price <= 0:
            await send_clean_message(update, context, LOCALIZATION[lang]['error'])
            return ОЖИДАНИЕ_ЦЕНЫ_ВЕС
        kg_price = (price / weight) * 1000
        price_100g = (price / weight) * 100
        await delete_mode_message(update, context)
        title = LOCALIZATION[lang]['calc_title_per_kg']
        result_text = LOCALIZATION[lang]['weight_result'].format(
            title=title, price=price, weight=weight, kg_price=kg_price, price_100g=price_100g
        )
        
        explanation = LOCALIZATION[lang]['expl_weight'].format(
            price=price, weight=weight, kg_price=kg_price
        )
        context.user_data['last_explanation'] = explanation

        await send_clean_message(update, context, result_text, reply_markup=get_result_keyboard(context), keep_result=True)
        add_to_history(context, result_text)
        context.user_data.pop('цена_веса', None)
        await send_clean_message(update, context, LOCALIZATION[lang]['next_action_prompt'], reply_markup=get_next_actions_keyboard(context))
        return ВЫБОР_ТИПА_СКИДКИ
    except ValueError:
        await send_clean_message(update, context, LOCALIZATION[lang]['invalid_number'], reply_markup=get_back_keyboard(context))
        return ОЖИДАНИЕ_ГРАММОВ

# --- ОБРАТНЫЙ РАСЧЕТ ---

async def calculate_original_price(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    lang = get_language(context)
    context.user_data['текущее_действие'] = 'menu_original_price'
    context.user_data['попередній_стан'] = ВЫБОР_ТИПА_СКИДКИ
    if update.callback_query:
        await update.callback_query.answer()
    mode_msg = await send_clean_message(update, context, LOCALIZATION[lang]['mode_original_price'], reply_markup=None, keep_result=True)
    context.user_data['mode_message_id'] = mode_msg.message_id
    await send_clean_message(
        update, 
        context, 
        LOCALIZATION[lang]['enter_price'], 
        reply_markup=get_back_to_menu_keyboard(context) 
    )
    return ОЖИДАНИЕ_ЦЕНЫ_СО_СКИДКОЙ

async def handle_discounted_price(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    lang = get_language(context)
    text = update.message.text.replace(',', '.')
    try:
        price = float(text)
        if price <= 0:
            await send_clean_message(update, context, LOCALIZATION[lang]['invalid_price'], reply_markup=get_back_to_menu_keyboard(context))
            return ОЖИДАНИЕ_ЦЕНЫ_СО_СКИДКОЙ
        context.user_data['цена_со_скидкой'] = price
        context.user_data['попередній_стан'] = ОЖИДАНИЕ_ЦЕНЫ_СО_СКИДКОЙ
        await send_clean_message(update, context, LOCALIZATION[lang]['enter_custom_discount'], reply_markup=get_back_keyboard(context))
        return ОЖИДАНИЕ_ПРОЦЕНТА_СКИДКИ
    except ValueError:
        await send_clean_message(update, context, LOCALIZATION[lang]['invalid_price'], reply_markup=get_back_to_menu_keyboard(context))
        return ОЖИДАНИЕ_ЦЕНЫ_СО_СКИДКОЙ

async def calculate_original_price_result(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    lang = get_language(context)
    text = update.message.text.replace(',', '.')
    try:
        discount_percent = float(text)
        if not (0 < discount_percent < 100):
            await send_clean_message(update, context, LOCALIZATION[lang]['invalid_discount'], reply_markup=get_back_keyboard(context))
            return ОЖИДАНИЕ_ПРОЦЕНТА_СКИДКИ
        discounted_price = context.user_data.get('цена_со_скидкой', 0)
        original_price = discounted_price / (1 - discount_percent / 100)
        await delete_mode_message(update, context)
        title = LOCALIZATION[lang]['calc_title_original_price']
        result_text = LOCALIZATION[lang]['price_result'].format(
            title=title, price=original_price, discount=discount_percent, extra="", discounted_price=discounted_price
        )
        
        explanation = LOCALIZATION[lang]['expl_original'].format(
            price=discounted_price, discount=discount_percent, result=original_price
        )
        context.user_data['last_explanation'] = explanation

        await send_clean_message(update, context, result_text, reply_markup=get_result_keyboard(context), keep_result=True)
        add_to_history(context, result_text)
        await send_clean_message(update, context, LOCALIZATION[lang]['next_action_prompt'], reply_markup=get_next_actions_keyboard(context))
        return ВЫБОР_ТИПА_СКИДКИ
    except ValueError:
        await send_clean_message(update, context, LOCALIZATION[lang]['invalid_discount'], reply_markup=get_back_keyboard(context))
        return ОЖИДАНИЕ_ПРОЦЕНТА_СКИДКИ

# --- МАРЖА И НАЦЕНКА ---

async def calculate_margin_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    lang = get_language(context)
    context.user_data['текущее_действие'] = 'menu_margin'
    context.user_data['попередній_стан'] = ВЫБОР_ТИПА_СКИДКИ
    
    if update.callback_query:
        await update.callback_query.answer()
    
    mode_msg = await send_clean_message(
        update, context, 
        LOCALIZATION[lang]['mode_margin'], 
        reply_markup=None, 
        keep_result=True
    )
    context.user_data['mode_message_id'] = mode_msg.message_id
    
    await send_clean_message(
        update, 
        context, 
        LOCALIZATION[lang]['margin_enter_cost'], 
        reply_markup=get_back_to_menu_keyboard(context) 
    )
    return ОЖИДАНИЕ_ЗАКУПКИ

async def handle_margin_cost_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    lang = get_language(context)
    try:
        val = float(update.message.text.replace(',', '.'))
        context.user_data['margin_cost'] = val
        context.user_data['попередній_стан'] = ОЖИДАНИЕ_ЗАКУПКИ
        await send_clean_message(update, context, LOCALIZATION[lang]['margin_enter_shelf'], reply_markup=get_back_keyboard(context))
        return ОЖИДАНИЕ_ПОЛКИ_МАРЖА
    except ValueError:
        await send_clean_message(update, context, LOCALIZATION[lang]['invalid_price'], reply_markup=get_back_to_menu_keyboard(context))
        return ОЖИДАНИЕ_ЗАКУПКИ

async def handle_margin_shelf_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    lang = get_language(context)
    try:
        shelf = float(update.message.text.replace(',', '.'))
        cost = context.user_data['margin_cost']
        profit = shelf - cost
        markup_val = (profit / cost * 100) if cost else 0
        margin_val = (profit / shelf * 100) if shelf else 0
        
        await delete_mode_message(update, context)
        res = f"📊 Маржа\n💰 Прибыль: {profit:.2f}\n📈 Наценка: {markup_val:.1f}%\n📉 Маржа: {margin_val:.1f}%"
        
        explanation = LOCALIZATION[lang]['expl_margin'].format(
            shelf=shelf, cost=cost, profit=profit, markup=markup_val, margin=margin_val
        )
        context.user_data['last_explanation'] = explanation

        await send_clean_message(update, context, res, keep_result=True, reply_markup=get_result_keyboard(context))
        add_to_history(context, res)
        await send_clean_message(update, context, LOCALIZATION[lang]['next_action_prompt'], reply_markup=get_next_actions_keyboard(context))
        return ВЫБОР_ТИПА_СКИДКИ
    except ValueError:
        await send_clean_message(update, context, LOCALIZATION[lang]['invalid_price'], reply_markup=get_back_keyboard(context))
        return ОЖИДАНИЕ_ПОЛКИ_МАРЖА

# --- ОБРАБОТЧИК КНОПКИ "ПОКАЗАТЬ РАСЧЕТ" ---

async def show_calculation_details(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    
    explanation = context.user_data.get('last_explanation')
    if not explanation:
        return

    # Получаем HTML-текст (чтобы сохранить форматирование оригинала)
    current_text = query.message.text_html
    lang = get_language(context)
    
    # Добавляем объяснение
    new_text = f"{current_text}{LOCALIZATION[lang]['expl_header']}{explanation}"
    
    try:
        # Меняем кнопку на "Скрыть"
        await query.edit_message_text(text=new_text, reply_markup=get_hide_result_keyboard(context), parse_mode='HTML')
    except Exception as e:
        logger.error(f"Error editing message: {e}")

async def hide_calculation_details(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    
    current_text = query.message.text_html
    lang = get_language(context)
    # Нам нужен заголовок из локализации, но в HTML формате (с <b>)
    header = LOCALIZATION[lang]['expl_header']

    # Разделяем текст по заголовку
    if header in current_text:
        original_text = current_text.split(header)[0]
        try:
            # Возвращаем исходный текст и кнопку "Показать"
            await query.edit_message_text(text=original_text, reply_markup=get_result_keyboard(context), parse_mode='HTML')
        except Exception as e:
            logger.error(f"Error hiding details: {e}")

# --- ОБЩИЕ ---

async def back(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()

    current_action = context.user_data.get('текущее_действие')
    prev_state = context.user_data.get('попередній_стан')

    if current_action == 'menu_shelf_discount':
        return await calculate_shelf_discount(update, context)

    elif current_action == 'menu_nx':
        if prev_state == ОЖИДАНИЕ_N:
             return await calculate_n_plus_x(update, context)
        if prev_state == ОЖИДАНИЕ_X:
             await send_clean_message(update, context, LOCALIZATION[get_language(context)]['enter_x'], reply_markup=get_back_keyboard(context))
             return ОЖИДАНИЕ_X
        return await calculate_n_plus_x(update, context)

    elif current_action == 'menu_per_kg':
        if prev_state == ОЖИДАНИЕ_ЦЕНЫ_ВЕС:
             return await calculate_price_per_kg(update, context)
        return await calculate_price_per_kg(update, context)

    elif current_action == 'menu_original_price':
        if prev_state == ОЖИДАНИЕ_ЦЕНЫ_СО_СКИДКОЙ:
             return await calculate_original_price(update, context)
        return await calculate_original_price(update, context)
    
    elif current_action == 'menu_margin':
        if prev_state == ОЖИДАНИЕ_ЗАКУПКИ:
            return await calculate_margin_start(update, context)
        return await calculate_margin_start(update, context)

    return await start(update, context)

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE | None) -> None:
    logger.error(f"Error: {context.error}")

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await send_clean_message(update, context, "Отмена", reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

async def restart(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if update.callback_query: await update.callback_query.answer()
    
    current_lang = context.user_data.get('language', 'ru')
    context.user_data.clear()
    context.user_data['language'] = current_lang
    
    return await start(update, context)

async def handle_unexpected_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    lang = get_language(context)
    if context.user_data.get("текущее_действие") == "menu_shelf_discount":
        try:
            val = float(update.message.text.replace(',', '.').replace('%', ''))
            if 0 < val < 100:
                context.user_data["скидка"] = val
                await send_clean_message(update, context, LOCALIZATION[lang]["enter_price"], reply_markup=get_back_keyboard(context))
                return ОЖИДАНИЕ_ЦЕНЫ
        except: pass
    await send_clean_message(update, context, LOCALIZATION[lang]["unexpected_text"])
    return ВЫБОР_ТИПА_СКИДКИ

# ===== ЗАПУСК =====

def get_application():
    if not TOKEN:
        raise ValueError("Токен не найден! Проверь переменные окружения.")
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_error_handler(error_handler)
    
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            ВЫБОР_ЯЗЫКА: [CallbackQueryHandler(choose_language, pattern="^lang_(ru|uk|en)$"), CommandHandler("start", start)],
            ВЫБОР_ТИПА_СКИДКИ: [
                CallbackQueryHandler(calculate_shelf_discount, pattern="^menu_shelf_discount$"),
                CallbackQueryHandler(calculate_n_plus_x, pattern="^menu_nx$"),
                CallbackQueryHandler(calculate_price_per_kg, pattern="^menu_per_kg$"),
                CallbackQueryHandler(calculate_original_price, pattern="^menu_original_price$"),
                CallbackQueryHandler(calculate_margin_start, pattern="^menu_margin$"),
                CallbackQueryHandler(handle_fixed_discount, pattern="^(5|10|15|20|25|30|35|40|45|50)$"),
                CallbackQueryHandler(custom_discount, pattern="^(другая_скидка|інша_знижка)$"),
                CallbackQueryHandler(settings_menu, pattern="^настройки$"),
                
                # ВОТ ЗДЕСЬ ДОБАВЛЕНА ПОДДЕРЖКА КНОПОК ПОКАЗАТЬ/СКРЫТЬ
                CallbackQueryHandler(show_calculation_details, pattern="^show_calc$"),
                CallbackQueryHandler(hide_calculation_details, pattern="^hide_calc$"),
                
                CallbackQueryHandler(restart, pattern="^to_menu$"),
                CallbackQueryHandler(restart, pattern="^перезапустить_бот$"),
                CommandHandler("start", restart),
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_unexpected_text),
            ],
            
            # ТАКЖЕ ДОБАВЛЕНА ПОДДЕРЖКА КНОПОК ВО ВСЕ ОСТАЛЬНЫЕ СОСТОЯНИЯ
            ОЖИДАНИЕ_СВОЕЙ_СКИДКИ: [MessageHandler(filters.TEXT, handle_discount_input), CallbackQueryHandler(back, pattern="^назад$")],
            ОЖИДАНИЕ_ЦЕНЫ: [MessageHandler(filters.TEXT, handle_price_input), CallbackQueryHandler(back, pattern="^назад$")],
            
            ОЖИДАНИЕ_N: [MessageHandler(filters.TEXT, handle_n_input), CallbackQueryHandler(restart, pattern="^to_menu$")],
            ОЖИДАНИЕ_X: [MessageHandler(filters.TEXT, handle_x_input), CallbackQueryHandler(back, pattern="^назад$")],
            ОЖИДАНИЕ_ЦЕНЫ_NX: [
                MessageHandler(filters.TEXT, handle_nx_price_input), 
                CallbackQueryHandler(back, pattern="^назад$"),
                CallbackQueryHandler(show_calculation_details, pattern="^show_calc$"),
                CallbackQueryHandler(hide_calculation_details, pattern="^hide_calc$")
            ],
            
            ОЖИДАНИЕ_ЦЕНЫ_ВЕС: [MessageHandler(filters.TEXT, handle_weight_price_input), CallbackQueryHandler(restart, pattern="^to_menu$")],
            ОЖИДАНИЕ_ГРАММОВ: [
                MessageHandler(filters.TEXT, handle_weight_input), 
                CallbackQueryHandler(back, pattern="^назад$"),
                CallbackQueryHandler(show_calculation_details, pattern="^show_calc$"),
                CallbackQueryHandler(hide_calculation_details, pattern="^hide_calc$")
            ],
            
            ОЖИДАНИЕ_ЦЕНЫ_СО_СКИДКОЙ: [MessageHandler(filters.TEXT, handle_discounted_price), CallbackQueryHandler(restart, pattern="^to_menu$")],
            ОЖИДАНИЕ_ПРОЦЕНТА_СКИДКИ: [
                MessageHandler(filters.TEXT, calculate_original_price_result), 
                CallbackQueryHandler(back, pattern="^назад$"),
                CallbackQueryHandler(show_calculation_details, pattern="^show_calc$"),
                CallbackQueryHandler(hide_calculation_details, pattern="^hide_calc$")
            ],
            
            ОЖИДАНИЕ_ЗАКУПКИ: [MessageHandler(filters.TEXT, handle_margin_cost_input), CallbackQueryHandler(restart, pattern="^to_menu$")],
            ОЖИДАНИЕ_ПОЛКИ_МАРЖА: [
                MessageHandler(filters.TEXT, handle_margin_shelf_input), 
                CallbackQueryHandler(back, pattern="^назад$"),
                CallbackQueryHandler(show_calculation_details, pattern="^show_calc$"),
                CallbackQueryHandler(hide_calculation_details, pattern="^hide_calc$")
            ],
            
            НАСТРОЙКИ: [
                CallbackQueryHandler(change_language, pattern="^сменить_язык$"), 
                CallbackQueryHandler(clear_chat_history, pattern="^clear_chat$"),
                CallbackQueryHandler(back, pattern="^назад$"),
                CallbackQueryHandler(restart, pattern="^to_menu$")
            ],
        },
        fallbacks=[
            CommandHandler("cancel", cancel), 
            CommandHandler("start", restart), 
            CallbackQueryHandler(restart, pattern="^перезапустить_бот$"),
            CallbackQueryHandler(show_calculation_details, pattern="^show_calc$"),
            CallbackQueryHandler(hide_calculation_details, pattern="^hide_calc$")
        ],
        per_chat=True
    )
    app.add_handler(conv_handler)
    return app

register_handlers = get_application
