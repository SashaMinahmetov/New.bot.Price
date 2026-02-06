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
    ОЖИДАНИЕ_ЗАКУПКИ,      # Для маржи (бывший PRO)
    ОЖИДАНИЕ_ПОЛКИ_МАРЖА,  # Для маржи (бывший PRO)
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
        'main_menu': "👋 Добро пожаловать! Выберите опцию для расчета:",
        'select_discount': "📦 Выберите процент скидки:",
        'enter_custom_discount': "🎯 Введите свой процент скидки (например, 14.44):",
        'enter_price': "🔢 Введите цену на полке (например, 545.44):",
        'price_result': "{title}\n\n💰 Цена на полке: {price:.2f} грн\n🎯 Скидка: {discount}%{extra}\n✅ Цена со скидкой: {discounted_price:.2f} грн",
        'invalid_discount': "❌ Ошибка. Скидка должна быть от 0% до 100%.",
        'invalid_price': "❌ Ошибка. Введите цену корректно, например: 545.44.",
        'enter_n': "🔢 Введите количество товаров, которые нужно купить (N):\n\nМожете выбрать цифру кнопками ниже.",
        'enter_x': "🎯 Введите количество бесплатных товаров (X):\n\nМожете выбрать цифру кнопками ниже.",
        'enter_nx_price': "💰 Введите цену одного товара (например, 99.99):",
        'nx_result': "{title}\n\n🛒 Акция: {n}+{x}\n💰 Цена одного товара: {price:.2f} грн\n💸 Общая сумма: {total:.2f} грн\n🎯 Фактичная скидка: {discount:.2f}%\n✅ Цена за единицу с учетом акции: {unit_price:.2f} грн",
        'enter_weight_price': "💰 Введите цену товара (например, 50.75):",
        'enter_weight': "⚖️ Введите количество грамм/мл в упаковке (например, 125):",
        'weight_result': '{title}\n\n💰 Цена: {price:.2f} грн\n⚖️ Вес: {weight:.2f} г/мл\n📊 Цена за 1 кг/л: {kg_price:.2f} грн\n📏 Цена за 100 г/мл: {price_100g:.2f} грн',
        'enter_price_short': 'Введите цену товара:',
        'enter_weight_short': 'Введите вес/объем (в граммах или мл):',
        'invalid_number': 'Пожалуйста, введите корректное число (больше 0).',
        'error': '❌ Произошла ошибка. Попробуйте снова или введите /start для перезапуска.',
        'cancel': "❌ Операция отменена. Введите /start для начала работы.",
        'restart': "🔄 Бот перезапущен!\n👋 Добро пожаловать! Выберите опцию для расчета:",
        'unexpected_text': "❌ Пожалуйста, используйте кнопки меню для выбора. Если вы хотите ввести свое значение, сначала выберите 'Другая %'.",
        'settings_menu': "⚙️ Настройки\nВыберите опцию:",
        'change_language': "🔄 Сменить язык",
        'back': "🔙 Назад",
        'next_action_prompt': "📊 Выберите следующее действие:",
        'restart_btn': "🔁 Перезапустить бот",
        'mode_shelf': "📦 Вы выбрали: «Сколько стоит со скидкой»",
        'mode_nx': "🎯 Вы выбрали: «Скидка по акции N+X»",
        'mode_per_kg': "⚖️ Вы выбрали: «Сколько за кг/литр»",
        'mode_original_price': "💼 Вы выбрали: «Узнать регулярную цену без скидки»",
        'mode_margin': "📊 Вы выбрали: «Маржа и наценка»",
        'calc_title_shelf': "📦 Сколько стоит со скидкой",
        'calc_title_nx': "🎯 Скидка по акции N+X",
        'calc_title_per_kg': "⚖️ Сколько за кг/литр",
        'calc_title_original_price': "💼 Узнать регулярную цену без скидки",
        'main_menu_btn': [
            ("📦 Сколько стоит со скидкой", "menu_shelf_discount"),
            ("🎯 Скидка по акции N+X", "menu_nx"),
            ("⚖️ Сколько за кг/литр", "menu_per_kg"),
            ("💼 Узнать регулярную цену без скидки", "menu_original_price"),
            ("📊 Маржа и наценка", "menu_margin"),
            ("⚙️ Настройки", "настройки"),
        ],
        'discount_buttons': [
            [("5%", "5"), ("10%", "10"), ("15%", "15"), ("20%", "20")],
            [("25%", "25"), ("30%", "30"), ("35%", "35"), ("40%", "40")],
            [("45%", "45"), ("50%", "50"), ("Другая %", "другая_скидка")]
        ],
        'margin_enter_cost': "💼 Введите закупочную цену товара:",
        'margin_enter_shelf': "🏷️ Введите цену товара на полке:",
    },
    'uk': {
        'welcome': "👋 Ласкаво просимо! Оберіть мову:",
        'main_menu': "👋 Ласкаво просимо! Оберіть опцію для розрахунку:",
        'select_discount': "📦 Оберіть відсоток знижки:",
        'enter_custom_discount': "🎯 Введіть свій відсоток знижки (наприклад, 14.44):",
        'enter_price': "🔢 Введіть ціну на полиці (наприклад, 545.44):",
        'price_result': "{title}\n\n💰 Ціна на полиці: {price:.2f} грн\n🎯 Знижка: {discount}%{extra}\n✅ Ціна зі знижкою: {discounted_price:.2f} грн",
        'invalid_discount': "❌ Помилка. Знижка має бути від 0% до 100%.",
        'invalid_price': "❌ Помилка. Введіть ціну коректно, наприклад: 545.44.",
        'enter_n': "🔢 Введіть кількість товарів, які потрібно купити (N):\n\nМожете обрати цифру кнопками нижче.",
        'enter_x': "🎯 Введіть кількість безкоштовних товарів (X):\n\nМожете обрати цифру кнопками нижче.",
        'enter_nx_price': "💰 Введіть ціну одного товару (наприклад, 99.99):",
        'nx_result': "{title}\n\n🛒 Акція: {n}+{x}\n💰 Ціна одного товару: {price:.2f} грн\n💸 Загальна сума: {total:.2f} грн\n🎯 Фактична знижка: {discount:.2f}%\n✅ Ціна за одиницю з урахуванням акції: {unit_price:.2f} грн",
        'enter_weight_price': "💰 Введіть ціну товару (наприклад, 50.75):",
        'enter_weight': "⚖️ Введіть кількість грамів/мл в упаковці (наприклад, 125):",
        'weight_result': '{title}\n\n💰 Ціна: {price:.2f} грн\n⚖️ Вага: {weight:.2f} г/мл\n📊 Ціна за 1 кг/л: {kg_price:.2f} грн\n📏 Ціна за 100 г/мл: {price_100g:.2f} грн',
        'enter_price_short': 'Введіть ціну товару:',
        'enter_weight_short': 'Введіть вагу/об’єм (у грамах або мл):',
        'invalid_number': 'Будь ласка, введіть коректне число (більше 0).',
        'error': '❌ Сталася помилка. Спробуйте ще раз або введіть /start для перезапуску.',
        'cancel': "❌ Операцію скасовано. Введіть /start для початку роботи.",
        'restart': "🔄 Бот перезапущено!\n👋 Ласкаво просимо! Оберіть опцію для розрахунку:",
        'unexpected_text': "❌ Будь ласка, використовуйте кнопки меню для вибору. Якщо хочете ввести власне значення, спочатку оберіть 'Інший %'.",
        'settings_menu': "⚙️ Налаштування\nОберіть опцію:",
        'change_language': "🔄 Змінити мову",
        'back': "🔙 Назад",
        'next_action_prompt': "📊 Оберіть наступну дію:",
        'restart_btn': "🔁 Перезапустити бота",
        'mode_shelf': "📦 Ви обрали: «Скільки коштує зі знижкою»",
        'mode_nx': "🎯 Ви обрали: «Знижка по акції N+X»",
        'mode_per_kg': "⚖️ Ви обрали: «Скільки за кг/літр»",
        'mode_original_price': "💼 Ви обрали: «Дізнатись регулярну ціну без знижки»",
        'mode_margin': "📊 Ви обрали: «Маржа та націнка»",
        'calc_title_shelf': "📦 Скільки коштує зі знижкою",
        'calc_title_nx': "🎯 Знижка по акції N+X",
        'calc_title_per_kg': "⚖️ Скільки за кг/літр",
        'calc_title_original_price': "💼 Дізнатись регулярну ціну без знижки",
        'main_menu_btn': [
            ("📦 Скільки коштує зі знижкою", "menu_shelf_discount"),
            ("🎯 Знижка по акції N+X", "menu_nx"),
            ("⚖️ Скільки за кг/літр", "menu_per_kg"),
            ("💼 Дізнатись регулярну ціну без знижки", "menu_original_price"),
            ("📊 Маржа та націнка", "menu_margin"),
            ("⚙️ Налаштування", "настройки"),
        ],
        'discount_buttons': [
            [("5%", "5"), ("10%", "10"), ("15%", "15"), ("20%", "20")],
            [("25%", "25"), ("30%", "30"), ("35%", "35"), ("40%", "40")],
            [("45%", "45"), ("50%", "50"), ("Інший %", "інша_знижка")]
        ],
        'margin_enter_cost': "💼 Введіть закупівельну ціну товару:",
        'margin_enter_shelf': "🏷️ Введіть ціну товару на полиці:",
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

    sent = await bot.send_message(chat_id=chat.id, text=text, reply_markup=reply_markup)

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
        [InlineKeyboardButton("Русский", callback_data="lang_ru")],
        [InlineKeyboardButton("Українська", callback_data="lang_uk")]
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
    keyboard.append([InlineKeyboardButton(LOCALIZATION[lang]['back'], callback_data="назад")])
    return InlineKeyboardMarkup(keyboard)

def get_settings_keyboard(context: ContextTypes.DEFAULT_TYPE):
    lang = get_language(context)
    keyboard = [
        [InlineKeyboardButton(LOCALIZATION[lang]['change_language'], callback_data="сменить_язык")],
        [InlineKeyboardButton(LOCALIZATION[lang]['back'], callback_data="назад")],
        [InlineKeyboardButton(LOCALIZATION[lang]['restart_btn'], callback_data="перезапустить_бот")],
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
    if 'language' not in context.user_data:
        context.user_data['попередній_стан'] = ВЫБОР_ЯЗЫКА
        await send_clean_message(
            update,
            context,
            "👋 Выберите язык / Оберіть мову:",
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
        "👋 Выберите язык / Оберіть мову:",
        reply_markup=get_language_keyboard()
    )
    return ВЫБОР_ЯЗЫКА

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
        reply_markup=None
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
        reply_markup=None
    )
    return ОЖИДАНИЕ_СВОЕЙ_СКИДКИ

async def handle_discount_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    lang = get_language(context)
    try:
        text = update.message.text.replace(',', '.')
        if not all(c.isdigit() or c == '.' for c in text):
            await send_clean_message(update, context, LOCALIZATION[lang]['invalid_discount'])
            return ОЖИДАНИЕ_СВОЕЙ_СКИДКИ

        discount = float(text)
        if discount <= 0 or discount >= 100:
            await send_clean_message(update, context, LOCALIZATION[lang]['invalid_discount'])
            return ОЖИДАНИЕ_СВОЕЙ_СКИДКИ

        context.user_data['скидка'] = discount
        context.user_data['попередній_стан'] = ОЖИДАНИЕ_СВОЕЙ_СКИДКИ

        await send_clean_message(
            update,
            context,
            LOCALIZATION[lang]['enter_price'],
            reply_markup=None
        )
        return ОЖИДАНИЕ_ЦЕНЫ
    except ValueError:
        await send_clean_message(update, context, LOCALIZATION[lang]['invalid_discount'])
        return ОЖИДАНИЕ_СВОЕЙ_СКИДКИ
    except Exception as e:
        logger.error(f"Error: {e}")
        await send_clean_message(update, context, LOCALIZATION[lang]['error'])
        return ОЖИДАНИЕ_СВОЕЙ_СКИДКИ

async def handle_price_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    lang = get_language(context)
    try:
        text = update.message.text.replace(',', '.')
        if not all(c.isdigit() or c == '.' for c in text):
            await send_clean_message(update, context, LOCALIZATION[lang]['invalid_price'])
            return ОЖИДАНИЕ_ЦЕНЫ

        price = float(text)
        if price <= 0:
            await send_clean_message(update, context, LOCALIZATION[lang]['invalid_price'])
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
        await send_clean_message(
            update,
            context,
            result_text,
            reply_markup=None,
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
        await send_clean_message(update, context, LOCALIZATION[lang]['invalid_price'])
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
        reply_markup=get_numeric_reply_keyboard()
    )
    return ОЖИДАНИЕ_N

async def handle_n_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    lang = get_language(context)
    text = update.message.text.strip()
    if not text.isdigit():
        await send_clean_message(update, context, LOCALIZATION[lang]['invalid_number'], reply_markup=get_numeric_reply_keyboard())
        return ОЖИДАНИЕ_N
    n = int(text)
    if n <= 0:
        await send_clean_message(update, context, LOCALIZATION[lang]['invalid_number'], reply_markup=get_numeric_reply_keyboard())
        return ОЖИДАНИЕ_N
    context.user_data['n'] = n
    context.user_data['попередній_стан'] = ОЖИДАНИЕ_N
    await send_clean_message(update, context, LOCALIZATION[lang]['enter_x'], reply_markup=get_numeric_reply_keyboard())
    return ОЖИДАНИЕ_X

async def handle_x_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    lang = get_language(context)
    text = update.message.text.strip()
    if not text.isdigit():
        await send_clean_message(update, context, LOCALIZATION[lang]['invalid_number'], reply_markup=get_numeric_reply_keyboard())
        return ОЖИДАНИЕ_X
    x = int(text)
    if x <= 0:
        await send_clean_message(update, context, LOCALIZATION[lang]['invalid_number'], reply_markup=get_numeric_reply_keyboard())
        return ОЖИДАНИЕ_X
    context.user_data['x'] = x
    context.user_data['попередній_стан'] = ОЖИДАНИЕ_X
    await send_clean_message(update, context, LOCALIZATION[lang]['enter_nx_price'], reply_markup=ReplyKeyboardRemove())
    return ОЖИДАНИЕ_ЦЕНЫ_NX

async def handle_nx_price_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    lang = get_language(context)
    text = update.message.text.replace(',', '.')
    try:
        price = float(text)
        if price <= 0:
            await send_clean_message(update, context, LOCALIZATION[lang]['invalid_price'])
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
        await send_clean_message(update, context, result_text, reply_markup=None, keep_result=True)
        add_to_history(context, result_text)
        await send_clean_message(update, context, LOCALIZATION[lang]['next_action_prompt'], reply_markup=get_next_actions_keyboard(context))
        return ВЫБОР_ТИПА_СКИДКИ
    except ValueError:
        await send_clean_message(update, context, LOCALIZATION[lang]['invalid_price'])
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
    await send_clean_message(update, context, LOCALIZATION[lang]['enter_weight_price'], reply_markup=None)
    return ОЖИДАНИЕ_ЦЕНЫ_ВЕС

async def handle_weight_price_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    lang = get_language(context)
    text = update.message.text.replace(',', '.')
    try:
        price = float(text)
        if price <= 0:
            await send_clean_message(update, context, LOCALIZATION[lang]['invalid_price'])
            return ОЖИДАНИЕ_ЦЕНЫ_ВЕС
        context.user_data['цена_веса'] = price
        context.user_data['попередній_стан'] = ОЖИДАНИЕ_ЦЕНЫ_ВЕС
        await send_clean_message(update, context, LOCALIZATION[lang]['enter_weight'], reply_markup=None)
        return ОЖИДАНИЕ_ГРАММОВ
    except ValueError:
        await send_clean_message(update, context, LOCALIZATION[lang]['invalid_price'])
        return ОЖИДАНИЕ_ЦЕНЫ_ВЕС

async def handle_weight_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    lang = get_language(context)
    text = update.message.text.replace(',', '.')
    try:
        weight = float(text)
        if weight <= 0:
            await send_clean_message(update, context, LOCALIZATION[lang]['invalid_number'])
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
        await send_clean_message(update, context, result_text, reply_markup=None, keep_result=True)
        add_to_history(context, result_text)
        context.user_data.pop('цена_веса', None)
        await send_clean_message(update, context, LOCALIZATION[lang]['next_action_prompt'], reply_markup=get_next_actions_keyboard(context))
        return ВЫБОР_ТИПА_СКИДКИ
    except ValueError:
        await send_clean_message(update, context, LOCALIZATION[lang]['invalid_number'])
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
    await send_clean_message(update, context, LOCALIZATION[lang]['enter_price'], reply_markup=None)
    return ОЖИДАНИЕ_ЦЕНЫ_СО_СКИДКОЙ

async def handle_discounted_price(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    lang = get_language(context)
    text = update.message.text.replace(',', '.')
    try:
        price = float(text)
        if price <= 0:
            await send_clean_message(update, context, LOCALIZATION[lang]['invalid_price'])
            return ОЖИДАНИЕ_ЦЕНЫ_СО_СКИДКОЙ
        context.user_data['цена_со_скидкой'] = price
        context.user_data['попередній_стан'] = ОЖИДАНИЕ_ЦЕНЫ_СО_СКИДКОЙ
        await send_clean_message(update, context, LOCALIZATION[lang]['enter_custom_discount'], reply_markup=None)
        return ОЖИДАНИЕ_ПРОЦЕНТА_СКИДКИ
    except ValueError:
        await send_clean_message(update, context, LOCALIZATION[lang]['invalid_price'])
        return ОЖИДАНИЕ_ЦЕНЫ_СО_СКИДКОЙ

async def calculate_original_price_result(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    lang = get_language(context)
    text = update.message.text.replace(',', '.')
    try:
        discount_percent = float(text)
        if not (0 < discount_percent < 100):
            await send_clean_message(update, context, LOCALIZATION[lang]['invalid_discount'])
            return ОЖИДАНИЕ_ПРОЦЕНТА_СКИДКИ
        discounted_price = context.user_data.get('цена_со_скидкой', 0)
        original_price = discounted_price / (1 - discount_percent / 100)
        await delete_mode_message(update, context)
        title = LOCALIZATION[lang]['calc_title_original_price']
        result_text = LOCALIZATION[lang]['price_result'].format(
            title=title, price=original_price, discount=discount_percent, extra="", discounted_price=discounted_price
        )
        await send_clean_message(update, context, result_text, reply_markup=None, keep_result=True)
        add_to_history(context, result_text)
        await send_clean_message(update, context, LOCALIZATION[lang]['next_action_prompt'], reply_markup=get_next_actions_keyboard(context))
        return ВЫБОР_ТИПА_СКИДКИ
    except ValueError:
        await send_clean_message(update, context, LOCALIZATION[lang]['invalid_discount'])
        return ОЖИДАНИЕ_ПРОЦЕНТА_СКИДКИ

# --- МАРЖА И НАЦЕНКА (перенесено из PRO) ---

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
    
    await send_clean_message(update, context, LOCALIZATION[lang]['margin_enter_cost'], reply_markup=None)
    return ОЖИДАНИЕ_ЗАКУПКИ

async def handle_margin_cost_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    lang = get_language(context)
    try:
        val = float(update.message.text.replace(',', '.'))
        context.user_data['margin_cost'] = val
        await send_clean_message(update, context, LOCALIZATION[lang]['margin_enter_shelf'], reply_markup=None)
        return ОЖИДАНИЕ_ПОЛКИ_МАРЖА
    except ValueError:
        await send_clean_message(update, context, LOCALIZATION[lang]['invalid_price'])
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
        
        await send_clean_message(update, context, res, keep_result=True)
        add_to_history(context, res)
        await send_clean_message(update, context, LOCALIZATION[lang]['next_action_prompt'], reply_markup=get_next_actions_keyboard(context))
        return ВЫБОР_ТИПА_СКИДКИ
    except ValueError:
        await send_clean_message(update, context, LOCALIZATION[lang]['invalid_price'])
        return ОЖИДАНИЕ_ПОЛКИ_МАРЖА

# --- ОБЩИЕ ---

async def back(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    lang = get_language(context)
    prev = context.user_data.get('попередній_стан', ВЫБОР_ТИПА_СКИДКИ)
    state_map = {
        ВЫБОР_ТИПА_СКИДКИ: start,
        ОЖИДАНИЕ_СВОЕЙ_СКИДКИ: calculate_shelf_discount,
        ОЖИДАНИЕ_ЦЕНЫ: calculate_shelf_discount,
        ОЖИДАНИЕ_N: start,
        ОЖИДАНИЕ_X: calculate_n_plus_x,
        ОЖИДАНИЕ_ЦЕНЫ_NX: handle_x_input,
        ОЖИДАНИЕ_ЦЕНЫ_ВЕС: start,
        ОЖИДАНИЕ_ГРАММОВ: calculate_price_per_kg,
        ОЖИДАНИЕ_ЦЕНЫ_СО_СКИДКОЙ: calculate_original_price,
        ОЖИДАНИЕ_ПРОЦЕНТА_СКИДКИ: handle_discounted_price,
        ОЖИДАНИЕ_ЗАКУПКИ: start,
        ОЖИДАНИЕ_ПОЛКИ_МАРЖА: calculate_margin_start,
        НАСТРОЙКИ: start,
        ВЫБОР_ЯЗЫКА: start,
    }
    handler = state_map.get(prev, start)
    return await handler(update, context)

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE | None) -> None:
    logger.error(f"Error: {context.error}")

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await send_clean_message(update, context, "Отмена", reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

async def restart(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if update.callback_query: await update.callback_query.answer()
    context.user_data.clear()
    context.user_data['language'] = 'ru'
    await start(update, context)
    return ВЫБОР_ЯЗЫКА

async def handle_unexpected_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    lang = get_language(context)
    if context.user_data.get("текущее_действие") == "menu_shelf_discount":
        try:
            val = float(update.message.text.replace(',', '.').replace('%', ''))
            if 0 < val < 100:
                context.user_data["скидка"] = val
                await send_clean_message(update, context, LOCALIZATION[lang]["enter_price"])
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
            ВЫБОР_ЯЗЫКА: [CallbackQueryHandler(choose_language, pattern="^lang_(ru|uk)$"), CommandHandler("start", start)],
            ВЫБОР_ТИПА_СКИДКИ: [
                CallbackQueryHandler(calculate_shelf_discount, pattern="^menu_shelf_discount$"),
                CallbackQueryHandler(calculate_n_plus_x, pattern="^menu_nx$"),
                CallbackQueryHandler(calculate_price_per_kg, pattern="^menu_per_kg$"),
                CallbackQueryHandler(calculate_original_price, pattern="^menu_original_price$"),
                CallbackQueryHandler(calculate_margin_start, pattern="^menu_margin$"),
                CallbackQueryHandler(handle_fixed_discount, pattern="^(5|10|15|20|25|30|35|40|45|50)$"),
                CallbackQueryHandler(custom_discount, pattern="^(другая_скидка|інша_знижка)$"),
                CallbackQueryHandler(settings_menu, pattern="^настройки$"),
                CallbackQueryHandler(restart, pattern="^перезапустить_бот$"),
                CommandHandler("start", restart),
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_unexpected_text),
            ],
            ОЖИДАНИЕ_СВОЕЙ_СКИДКИ: [MessageHandler(filters.TEXT, handle_discount_input), CallbackQueryHandler(back, pattern="^назад$")],
            ОЖИДАНИЕ_ЦЕНЫ: [MessageHandler(filters.TEXT, handle_price_input), CallbackQueryHandler(back, pattern="^назад$")],
            ОЖИДАНИЕ_N: [MessageHandler(filters.TEXT, handle_n_input)],
            ОЖИДАНИЕ_X: [MessageHandler(filters.TEXT, handle_x_input)],
            ОЖИДАНИЕ_ЦЕНЫ_NX: [MessageHandler(filters.TEXT, handle_nx_price_input), CallbackQueryHandler(back, pattern="^назад$")],
            ОЖИДАНИЕ_ЦЕНЫ_ВЕС: [MessageHandler(filters.TEXT, handle_weight_price_input), CallbackQueryHandler(back, pattern="^назад$")],
            ОЖИДАНИЕ_ГРАММОВ: [MessageHandler(filters.TEXT, handle_weight_input), CallbackQueryHandler(back, pattern="^назад$")],
            ОЖИДАНИЕ_ЦЕНЫ_СО_СКИДКОЙ: [MessageHandler(filters.TEXT, handle_discounted_price), CallbackQueryHandler(back, pattern="^назад$")],
            ОЖИДАНИЕ_ПРОЦЕНТА_СКИДКИ: [MessageHandler(filters.TEXT, calculate_original_price_result), CallbackQueryHandler(back, pattern="^назад$")],
            ОЖИДАНИЕ_ЗАКУПКИ: [MessageHandler(filters.TEXT, handle_margin_cost_input), CallbackQueryHandler(back, pattern="^назад$")],
            ОЖИДАНИЕ_ПОЛКИ_МАРЖА: [MessageHandler(filters.TEXT, handle_margin_shelf_input), CallbackQueryHandler(back, pattern="^назад$")],
            НАСТРОЙКИ: [CallbackQueryHandler(change_language, pattern="^сменить_язык$"), CallbackQueryHandler(back, pattern="^назад$")],
        },
        fallbacks=[CommandHandler("cancel", cancel), CommandHandler("start", restart), CallbackQueryHandler(restart, pattern="^перезапустить_бот$")],
        per_chat=True
    )
    app.add_handler(conv_handler)
    return app

register_handlers = get_application
