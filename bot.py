import os
import logging
import re
import asyncio
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
    WebAppInfo,  # <--- Добавили для Mini App
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
# ССЫЛКА НА ТВОЙ MINI APP (Замени на свою!)
MINI_APP_URL = "https://t.me/e_discount_bot/app" 

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
    ОЖИДАНИЕ_ЗАКУПКИ,      
    ОЖИДАНИЕ_ПОЛКИ_МАРЖА,  
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
        'welcome': "👋 <b>Добро пожаловать!</b>\nВыберите язык интерфейса:",
        'main_menu': "🧮 <b>Главное меню</b>\nВыберите нужный расчет или откройте приложение:",
        'select_discount': "📉 <b>Выберите размер скидки:</b>",
        'enter_custom_discount': "🎯 <b>Введите свою скидку (%):</b>\n<i>Например: 15 или 14.5</i>",
        'enter_price': "🏷 <b>Введите цену на полке:</b>\n<i>Например: 545.00</i>",
        
        # Обновленный красивый дизайн результата (Стиль Чека)
        'price_result': (
            "{title}\n\n"
            "💵 Цена:    <code>{price:.2f} ₴</code>\n"
            "🔻 Скидка:  <code>{discount}%</code>{extra}\n"
            "──────────────\n"
            "✅ <b>ИТОГО:</b>   <code>{discounted_price:.2f} ₴</code>"
        ),
        
        'invalid_discount': "❌ <b>Ошибка!</b> Скидка должна быть от 0% до 100%.",
        'invalid_price': "❌ <b>Ошибка!</b> Введите корректное число (например: <code>545.44</code>).",
        
        'enter_n': "🔢 <b>Количество к покупке (N):</b>",
        'enter_x': "🎁 <b>Количество в подарок (X):</b>",
        'enter_nx_price': "💰 <b>Цена за одну штуку:</b>",
        
        'nx_result': (
            "{title}\n\n"
            "🛍 Акция:    <code>{n}+{x}</code>\n"
            "🏷 Цена шт:  <code>{price:.2f} ₴</code>\n"
            "──────────────\n"
            "📦 Всего шт: <code>{total:.2f} ₴</code>\n"
            "📉 Выгода:   <code>{discount:.1f}%</code>\n"
            "✅ <b>Цена за 1:</b> <code>{unit_price:.2f} ₴</code>"
        ),

        'enter_weight_price': "💰 <b>Цена за упаковку:</b>",
        'enter_weight': "⚖️ <b>Вес/объем (граммы или мл):</b>",
        
        'weight_result': (
            "{title}\n\n"
            "📦 Вес:      <code>{weight:.2f} г/мл</code>\n"
            "🏷 Цена:     <code>{price:.2f} ₴</code>\n"
            "──────────────\n"
            "📊 <b>За 1 кг/л:</b> <code>{kg_price:.2f} ₴</code>\n"
            "📏 За 100 г:   <code>{price_100g:.2f} ₴</code>"
        ),

        'enter_price_short': 'Введите цену товара:',
        'enter_weight_short': 'Введите вес (г) или объем (мл):',
        'invalid_number': 'Пожалуйста, введите корректное число больше 0.',
        'error': '❌ Произошла ошибка. Введите /start.',
        'cancel': "❌ Отменено. Введите /start.",
        'restart': "🔄 Бот перезапущен!",
        'unexpected_text': "⚠️ <b>Пожалуйста, используйте кнопки меню.</b>",
        'settings_menu': "⚙️ <b>Настройки:</b>",
        'change_language': "🌐 Сменить язык",
        'clear_chat_btn': "🗑 Очистить историю",
        'chat_cleared': "✅ <b>История переписки удалена!</b>",
        'back': "🔙 Назад",
        'back_to_menu_btn': "🏠 В меню",
        'next_action_prompt': "📊 <b>Что считаем дальше?</b>",
        'restart_btn': "🔄 Перезапуск",
        'btn_show_calc': "📝 Показать формулу",
        'btn_hide_calc': "🙈 Скрыть формулу",
        'btn_miniapp': "📱 Открыть Приложение", # Кнопка Mini App
        
        'expl_header': "\n\n📝 <b>Детали расчета:</b>\n",
        'expl_shelf': "<code>{price} - ({price} × {discount} / 100) = </code><b>{result:.2f}</b>",
        'expl_nx': "1. Всего товаров: {n} + {x} = <b>{total_qty}</b>\n2. Платим за {n}: {price} × {n} = <b>{total_sum:.2f}</b>\n3. Цена за шт: {total_sum:.2f} / {total_qty} = <b>{unit_price:.2f}</b>",
        'expl_weight': "<code>({price} / {weight}) × 1000 = </code><b>{kg_price:.2f}</b>",
        'expl_original': "<code>{price} / (1 - {discount} / 100) = </code><b>{result:.2f}</b>",
        'expl_margin': "• Прибыль: {shelf} - {cost} = <b>{profit:.2f}</b>\n• Наценка: ({profit:.2f} / {cost}) × 100 = <b>{markup:.1f}%</b>\n• Маржа: ({profit:.2f} / {shelf}) × 100 = <b>{margin:.1f}%</b>",

        'mode_shelf': "🏷 <b>Цена со скидкой</b>",
        'mode_nx': "🎁 <b>Акция N+X</b>",
        'mode_per_kg': "⚖️ <b>Цена за кг/л</b>",
        'mode_original_price': "🔙 <b>Поиск цены без скидки</b>",
        'mode_margin': "📊 <b>Маржа и Наценка</b>",
        
        'calc_title_shelf': "🏷 ЦЕНА СО СКИДКОЙ",
        'calc_title_nx': "🎁 АКЦИЯ N+X",
        'calc_title_per_kg': "⚖️ ЦЕНА ЗА КГ/Л",
        'calc_title_original_price': "🔙 ИСХОДНАЯ ЦЕНА",
        
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
        'margin_enter_cost': "💼 <b>Введите цену закупки:</b>",
        'margin_enter_shelf': "🏷️ <b>Введите цену на полке:</b>",
    },
    'uk': {
        'welcome': "👋 <b>Ласкаво просимо!</b>\nОберіть мову інтерфейсу:",
        'main_menu': "🧮 <b>Головне меню</b>\nОберіть розрахунок або відкрийте додаток:",
        'select_discount': "📉 <b>Оберіть відсоток знижки:</b>",
        'enter_custom_discount': "🎯 <b>Введіть свою знижку (%):</b>\n<i>Наприклад: 15 або 14.5</i>",
        'enter_price': "🏷 <b>Введіть ціну на полиці:</b>\n<i>Наприклад: 545.00</i>",
        
        'price_result': (
            "{title}\n\n"
            "💵 Ціна:     <code>{price:.2f} ₴</code>\n"
            "🔻 Знижка:   <code>{discount}%</code>{extra}\n"
            "──────────────\n"
            "✅ <b>РАЗОМ:</b>    <code>{discounted_price:.2f} ₴</code>"
        ),
        
        'invalid_discount': "❌ <b>Помилка!</b> Знижка має бути від 0% до 100%.",
        'invalid_price': "❌ <b>Помилка!</b> Введіть коректне число (наприклад: <code>545.44</code>).",
        'enter_n': "🔢 <b>Кількість до покупки (N):</b>",
        'enter_x': "🎁 <b>Кількість у подарунок (X):</b>",
        'enter_nx_price': "💰 <b>Ціна за одну штуку:</b>",
        
        'nx_result': (
            "{title}\n\n"
            "🛍 Акція:    <code>{n}+{x}</code>\n"
            "🏷 Ціна шт:  <code>{price:.2f} ₴</code>\n"
            "──────────────\n"
            "📦 Всього:   <code>{total:.2f} ₴</code>\n"
            "📉 Вигода:   <code>{discount:.1f}%</code>\n"
            "✅ <b>Ціна за 1:</b> <code>{unit_price:.2f} ₴</code>"
        ),

        'enter_weight_price': "💰 <b>Ціна за упаковку:</b>",
        'enter_weight': "⚖️ <b>Вага/об'єм (грами або мл):</b>",
        
        'weight_result': (
            "{title}\n\n"
            "📦 Вага:     <code>{weight:.2f} г/мл</code>\n"
            "🏷 Ціна:     <code>{price:.2f} ₴</code>\n"
            "──────────────\n"
            "📊 <b>За 1 кг/л:</b> <code>{kg_price:.2f} ₴</code>\n"
            "📏 За 100 г:   <code>{price_100g:.2f} ₴</code>"
        ),

        'enter_price_short': 'Введіть ціну товару:',
        'enter_weight_short': 'Введіть вагу (г) або об\'єм (мл):',
        'invalid_number': 'Будь ласка, введіть коректне число більше 0.',
        'error': '❌ Помилка. Введіть /start.',
        'cancel': "❌ Скасовано. Введіть /start.",
        'restart': "🔄 Бот перезапущено!",
        'unexpected_text': "⚠️ <b>Будь ласка, використовуйте кнопки меню.</b>",
        'settings_menu': "⚙️ <b>Налаштування:</b>",
        'change_language': "🌐 Змінити мову",
        'clear_chat_btn': "🗑 Очистити історію",
        'chat_cleared': "✅ <b>Історія повідомлень видалена!</b>",
        'back': "🔙 Назад",
        'back_to_menu_btn': "🏠 В меню",
        'next_action_prompt': "📊 <b>Що рахуємо далі?</b>",
        'restart_btn': "🔄 Перезапуск",
        'btn_show_calc': "📝 Показати формулу",
        'btn_hide_calc': "🙈 Приховати формулу",
        'btn_miniapp': "📱 Відкрити Додаток",

        'expl_header': "\n\n📝 <b>Деталі розрахунку:</b>\n",
        'expl_shelf': "<code>{price} - ({price} × {discount} / 100) = </code><b>{result:.2f}</b>",
        'expl_nx': "1. Всього товарів: {n} + {x} = <b>{total_qty}</b>\n2. Платимо за {n}: {price} × {n} = <b>{total_sum:.2f}</b>\n3. Ціна за шт: {total_sum:.2f} / {total_qty} = <b>{unit_price:.2f}</b>",
        'expl_weight': "<code>({price} / {weight}) × 1000 = </code><b>{kg_price:.2f}</b>",
        'expl_original': "<code>{price} / (1 - {discount} / 100) = </code><b>{result:.2f}</b>",
        'expl_margin': "• Прибуток: {shelf} - {cost} = <b>{profit:.2f}</b>\n• Націнка: ({profit:.2f} / {cost}) × 100 = <b>{markup:.1f}%</b>\n• Маржа: ({profit:.2f} / {shelf}) × 100 = <b>{margin:.1f}%</b>",

        'mode_shelf': "🏷 <b>Розрахунок ціни зі знижкою</b>",
        'mode_nx': "🎁 <b>Розрахунок акції N+X</b>",
        'mode_per_kg': "⚖️ <b>Розрахунок ціни за кг/л</b>",
        'mode_original_price': "🔙 <b>Пошук вихідної ціни</b>",
        'mode_margin': "📊 <b>Розрахунок маржі та націнки</b>",
        
        'calc_title_shelf': "🏷 ЦІНА ЗІ ЗНИЖКОЮ",
        'calc_title_nx': "🎁 АКЦІЯ N+X",
        'calc_title_per_kg': "⚖️ ЦІНА ЗА КГ/Л",
        'calc_title_original_price': "🔙 ВИХІДНА ЦІНА",
        
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
        'margin_enter_cost': "💼 <b>Введіть закупівельну ціну:</b>",
        'margin_enter_shelf': "🏷️ <b>Введіть ціну на полиці:</b>",
    },
    'en': {
        'welcome': "👋 <b>Welcome!</b>\nChoose your language:",
        'main_menu': "🧮 <b>Main Menu</b>\nChoose calculation or open App:",
        'select_discount': "📉 <b>Select discount percentage:</b>",
        'enter_custom_discount': "🎯 <b>Enter custom discount (%):</b>\n<i>Example: 15 or 14.5</i>",
        'enter_price': "🏷 <b>Enter shelf price:</b>\n<i>Example: 545.00</i>",
        
        'price_result': (
            "{title}\n\n"
            "💵 Price:    <code>{price:.2f}</code>\n"
            "🔻 Discount: <code>{discount}%</code>{extra}\n"
            "──────────────\n"
            "✅ <b>TOTAL:</b>    <code>{discounted_price:.2f}</code>"
        ),
        
        'invalid_discount': "❌ <b>Error!</b> Discount must be between 0% and 100%.",
        'invalid_price': "❌ <b>Error!</b> Please enter a valid number (e.g. <code>545.44</code>).",
        'enter_n': "🔢 <b>Enter quantity to buy (N):</b>",
        'enter_x': "🎁 <b>Enter free quantity (X):</b>",
        'enter_nx_price': "💰 <b>Price per item:</b>",
        
        'nx_result': (
            "{title}\n\n"
            "🛍 Promo:    <code>{n}+{x}</code>\n"
            "🏷 Item Price: <code>{price:.2f}</code>\n"
            "──────────────\n"
            "📦 Total:    <code>{total:.2f}</code>\n"
            "📉 Real Disc: <code>{discount:.1f}%</code>\n"
            "✅ <b>Unit Price:</b> <code>{unit_price:.2f}</code>"
        ),

        'enter_weight_price': "💰 <b>Enter pack price:</b>",
        'enter_weight': "⚖️ <b>Enter weight/volume (g or ml):</b>",
        
        'weight_result': (
            "{title}\n\n"
            "📦 Pack:     <code>{weight:.2f} g/ml</code>\n"
            "🏷 Price:    <code>{price:.2f}</code>\n"
            "──────────────\n"
            "📊 <b>Per 1 kg/l:</b> <code>{kg_price:.2f}</code>\n"
            "📏 Per 100 g:  <code>{price_100g:.2f}</code>"
        ),

        'enter_price_short': 'Enter item price:',
        'enter_weight_short': 'Enter weight (g) or volume (ml):',
        'invalid_number': 'Please enter a valid number greater than 0.',
        'error': '❌ Error. Type /start.',
        'cancel': "❌ Canceled. Type /start.",
        'restart': "🔄 Bot restarted!",
        'unexpected_text': "⚠️ <b>Please use menu buttons.</b>",
        'settings_menu': "⚙️ <b>Settings:</b>",
        'change_language': "🌐 Change Language",
        'clear_chat_btn': "🗑 Clear Chat History",
        'chat_cleared': "✅ <b>Chat history cleared!</b>",
        'back': "🔙 Back",
        'back_to_menu_btn': "🏠 Menu",
        'next_action_prompt': "📊 <b>What's next?</b>",
        'restart_btn': "🔄 Restart Bot",
        'btn_show_calc': "📝 Show Formula",
        'btn_hide_calc': "🙈 Hide Formula",
        'btn_miniapp': "📱 Open App",

        'expl_header': "\n\n📝 <b>Details:</b>\n",
        'expl_shelf': "<code>{price} - ({price} × {discount} / 100) = </code><b>{result:.2f}</b>",
        'expl_nx': "1. Total: {n} + {x} = <b>{total_qty}</b>\n2. Pay for {n}: {price} × {n} = <b>{total_sum:.2f}</b>\n3. Unit price: {total_sum:.2f} / {total_qty} = <b>{unit_price:.2f}</b>",
        'expl_weight': "<code>({price} / {weight}) × 1000 = </code><b>{kg_price:.2f}</b>",
        'expl_original': "<code>{price} / (1 - {discount} / 100) = </code><b>{result:.2f}</b>",
        'expl_margin': "• Profit: {shelf} - {cost} = <b>{profit:.2f}</b>\n• Markup: ({profit:.2f} / {cost}) × 100 = <b>{markup:.1f}%</b>\n• Margin: ({profit:.2f} / {shelf}) × 100 = <b>{margin:.1f}%</b>",

        'mode_shelf': "🏷 <b>Discount Calculator</b>",
        'mode_nx': "🎁 <b>N+X Promo</b>",
        'mode_per_kg': "⚖️ <b>Price per kg/l</b>",
        'mode_original_price': "🔙 <b>Reverse Price</b>",
        'mode_margin': "📊 <b>Margin & Markup</b>",
        
        'calc_title_shelf': "🏷 DISCOUNT PRICE",
        'calc_title_nx': "🎁 PROMO N+X",
        'calc_title_per_kg': "⚖️ PRICE PER KG/L",
        'calc_title_original_price': "🔙 ORIGINAL PRICE",
        
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
        'margin_enter_cost': "💼 <b>Enter cost price:</b>",
        'margin_enter_shelf': "🏷️ <b>Enter shelf price:</b>",
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
    parse_mode: str = 'HTML' # По умолчанию HTML
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
    # 1. Сначала кнопка Mini App
    keyboard = [[InlineKeyboardButton(
        text=LOCALIZATION[lang]['btn_miniapp'], 
        web_app=WebAppInfo(url=MINI_APP_URL)
    )]]
    
    # 2. Потом остальные кнопки
    for text, data in LOCALIZATION[lang]['main_menu_btn']:
        keyboard.append([InlineKeyboardButton(text, callback_data=data)])
        
    return InlineKeyboardMarkup(keyboard)

def get_next_actions_keyboard(context: ContextTypes.DEFAULT_TYPE):
    lang = get_language(context)
    # В "Что дальше" Mini App не обязателен, но можно добавить. Пока оставим расчеты.
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
    lang = get_language(context)
    keyboard = [
        [InlineKeyboardButton(LOCALIZATION[lang]['btn_show_calc'], callback_data="show_calc")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_hide_result_keyboard(context: ContextTypes.DEFAULT_TYPE):
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
            "👋 <b>Welcome!</b>\nВыберите язык / Оберіть мову / Choose language:",
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
        "👋 <b>Change Language</b>\nВыберите язык / Оберіть мову / Choose language:",
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
        text=LOCALIZATION[lang]['chat_cleared'],
        parse_mode='HTML'
    )
    
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
    # Мы убрали логику автоматического перехода в скидки.
    # Теперь бот просто просит нажать кнопку.
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
                
                # Обработчики показать/скрыть расчет (глобальные для этого меню)
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
            # Глобальные обработчики
            CallbackQueryHandler(show_calculation_details, pattern="^show_calc$"),
            CallbackQueryHandler(hide_calculation_details, pattern="^hide_calc$")
        ],
        per_chat=True
    )
    app.add_handler(conv_handler)
    return app

register_handlers = get_application
