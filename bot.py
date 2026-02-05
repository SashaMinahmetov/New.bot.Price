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

# Состояния диалога (Оставляем вашу структуру)
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
    НАСТРОЙКИ,
    PRO_MENU,
    PRO_AUTOMODE_INPUT,
    PRO_FIXED_PRICE,
    PRO_FIXED_DISCOUNT,
    PRO_LOYAL_ORIGINAL,
    PRO_LOYAL_CARD,
    PRO_DOUBLE_PRICE,
    PRO_DOUBLE_DISC1,
    PRO_DOUBLE_DISC2,
    PRO_COMPARE_FIRST_PRICE,
    PRO_COMPARE_FIRST_WEIGHT,
    PRO_COMPARE_SECOND_PRICE,
    PRO_COMPARE_SECOND_WEIGHT,
    PRO_PROMO_OLD,
    PRO_PROMO_NEW,
    PRO_MARGIN_COST,
    PRO_MARGIN_SHELF,
) = range(29)

# Настройка логирования
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# --- ЛОКАЛИЗАЦИЯ ---
# Мы добавили ключи 'buttons' для нижнего меню
LOCALIZATION = {
    'ru': {
        'buttons': {
            'shelf': "📦 Скидка %",
            'nx': "🎯 Акция N+X",
            'kg': "⚖️ Цена за кг/л",
            'orig': "🔙 Найти исх. цену",
            'pro': "🌟 PRO режим",
            'settings': "⚙️ Настройки",
            'restart': "🔁 Перезапуск"
        },
        'welcome': "👋 Добро пожаловать! Выберите раздел в меню снизу:",
        'main_menu': "👇 **Главное меню**\nВыберите нужный режим на клавиатуре снизу:",
        'select_discount': "📦 **Режим: Скидка**\nВыберите процент кнопками или введите свой:",
        'enter_custom_discount': "🎯 Введите свой процент скидки (например, 14.44):",
        'enter_price': "🔢 Введите цену на полке (например, 545.44):",
        'price_result': "{title}\n\n💰 Цена на полке: {price:.2f} грн\n🎯 Скидка: {discount}%{extra}\n✅ Цена со скидкой: {discounted_price:.2f} грн",
        'invalid_discount': "❌ Ошибка. Скидка должна быть от 0% до 100%.",
        'invalid_price': "❌ Ошибка. Введите цену корректно (число).",
        'enter_n': "🔢 **Режим N+X**\nСколько товаров берем (N)? (Ведите число)",
        'enter_x': "🎯 Сколько из них бесплатно (X)?",
        'enter_nx_price': "💰 Введите цену одного товара:",
        'nx_result': "{title}\n\n🛒 Акция: {n}+{x}\n💰 Цена одного: {price:.2f} грн\n💸 Всего за {n} шт: {total:.2f} грн\n🎯 Реальная скидка: {discount:.2f}%\n✅ **1 шт выходит: {unit_price:.2f} грн**",
        'enter_weight_price': "💰 **Режим: Вес**\nВведите цену товара:",
        'enter_weight': "⚖️ Введите вес (грамм/мл):",
        'weight_result': '{title}\n\n💰 Цена: {price:.2f} грн\n⚖️ Вес: {weight:.2f} г/мл\n📊 Цена за 1 кг/л: {kg_price:.2f} грн\n📏 Цена за 100 г/мл: {price_100g:.2f} грн',
        'invalid_number': 'Пожалуйста, введите корректное число.',
        'error': '❌ Ошибка.',
        'cancel': "❌ Отмена.",
        'unexpected_text': "👇 Пожалуйста, выберите режим в меню снизу.",
        'settings_menu': "⚙️ Настройки:",
        'change_language': "🔄 Сменить язык",
        'back': "🔙 Назад в меню",
        'next_action_prompt': "👇 Выберите следующее действие в меню:",
        'calc_title_shelf': "📦 Расчет скидки",
        'calc_title_nx': "🎯 Расчет N+X",
        'calc_title_per_kg': "⚖️ Расчет веса",
        'calc_title_original_price': "💼 Поиск цены без скидки",
        # Для PRO режима оставляем тексты как есть
        'mode_pro_auto': "🌟 PRO: Авто-режим",
        'mode_pro_fixed': "🌟 PRO: Фикс. скидка",
        'mode_pro_loyal': "🌟 PRO: Карта лояльности",
        'mode_pro_double': "🌟 PRO: Двойная скидка",
        'mode_pro_compare': "🌟 PRO: Сравнение товаров",
        'mode_pro_promo': "🌟 PRO: Сравнение промо",
        'mode_pro_margin': "🌟 PRO: Маржа",
        'mode_pro_history': "🌟 PRO: История",
        'pro_menu_title': "🌟 PRO режим. Выберите функцию:",
        'pro_btn_auto': "🤖 Авто",
        'pro_btn_fixed': "💸 Фикс",
        'pro_btn_loyal': "💳 Карта",
        'pro_btn_double': "🔁 Двойная",
        'pro_btn_compare': "⚖️ Сравнить",
        'pro_btn_promo': "📉 Промо",
        'pro_btn_margin': "📊 Маржа",
        'pro_btn_history': "📜 История",
        'pro_enter_expression': "✍️ Введите выражение (299-40% или 2+1 цена 60):",
        'pro_fixed_enter_price': "💰 Введите цену:",
        'pro_fixed_enter_discount_sum': "💸 Введите сумму скидки:",
        'pro_loyal_enter_regular': "💰 Цена без карты:",
        'pro_loyal_enter_card': "💳 Цена по карте:",
        'pro_double_enter_price': "💰 Цена товара:",
        'pro_double_enter_first': "🔁 Первая скидка (%):",
        'pro_double_enter_second': "🔁 Вторая скидка (%):",
        'pro_compare_first_price': "1️⃣ Цена товара 1:",
        'pro_compare_first_weight': "1️⃣ Вес товара 1:",
        'pro_compare_second_price': "2️⃣ Цена товара 2:",
        'pro_compare_second_weight': "2️⃣ Вес товара 2:",
        'pro_promo_old_price': "💵 Старая цена:",
        'pro_promo_new_price': "💸 Новая цена:",
        'pro_margin_cost': "💼 Закупка:",
        'pro_margin_shelf': "🏷️ Полка:",
        'pro_history_empty': "История пуста.",
        'pro_history_title': "📜 История:",
        'pro_auto_unknown': "⚠️ Не понял формат.",
        'discount_buttons': [
            [("5%", "5"), ("10%", "10"), ("15%", "15"), ("20%", "20")],
            [("25%", "25"), ("30%", "30"), ("35%", "35"), ("40%", "40")],
            [("45%", "45"), ("50%", "50"), ("Другая %", "другая_скидка")]
        ],
    },
    'uk': {
        'buttons': {
            'shelf': "📦 Знижка %",
            'nx': "🎯 Акція N+X",
            'kg': "⚖️ Ціна за кг/л",
            'orig': "🔙 Знайти вих. ціну",
            'pro': "🌟 PRO режим",
            'settings': "⚙️ Налаштування",
            'restart': "🔁 Перезапуск"
        },
        'welcome': "👋 Ласкаво просимо! Оберіть розділ в меню знизу:",
        'main_menu': "👇 **Головне меню**\nОберіть потрібний режим на клавіатурі знизу:",
        'select_discount': "📦 **Режим: Знижка**\nОберіть відсоток кнопками або введіть свій:",
        'enter_custom_discount': "🎯 Введіть свій відсоток знижки (наприклад, 14.44):",
        'enter_price': "🔢 Введіть ціну на полиці (наприклад, 545.44):",
        'price_result': "{title}\n\n💰 Ціна на полиці: {price:.2f} грн\n🎯 Знижка: {discount}%{extra}\n✅ Ціна зі знижкою: {discounted_price:.2f} грн",
        'invalid_discount': "❌ Помилка. Знижка має бути від 0% до 100%.",
        'invalid_price': "❌ Помилка. Введіть ціну коректно (число).",
        'enter_n': "🔢 **Режим N+X**\nСкільки товарів беремо (N)? (Введіть число)",
        'enter_x': "🎯 Скільки з них безкоштовно (X)?",
        'enter_nx_price': "💰 Введіть ціну одного товару:",
        'nx_result': "{title}\n\n🛒 Акція: {n}+{x}\n💰 Ціна одного: {price:.2f} грн\n💸 Всього за {n} шт: {total:.2f} грн\n🎯 Реальна знижка: {discount:.2f}%\n✅ **1 шт виходить: {unit_price:.2f} грн**",
        'enter_weight_price': "💰 **Режим: Вага**\nВведіть ціну товару:",
        'enter_weight': "⚖️ Введіть вагу (грам/мл):",
        'weight_result': '{title}\n\n💰 Ціна: {price:.2f} грн\n⚖️ Вага: {weight:.2f} г/мл\n📊 Ціна за 1 кг/л: {kg_price:.2f} грн\n📏 Ціна за 100 г/мл: {price_100g:.2f} грн',
        'invalid_number': 'Будь ласка, введіть коректне число.',
        'error': '❌ Помилка.',
        'cancel': "❌ Скасування.",
        'unexpected_text': "👇 Будь ласка, оберіть режим в меню знизу.",
        'settings_menu': "⚙️ Налаштування:",
        'change_language': "🔄 Змінити мову",
        'back': "🔙 Назад в меню",
        'next_action_prompt': "👇 Оберіть наступну дію в меню:",
        'calc_title_shelf': "📦 Розрахунок знижки",
        'calc_title_nx': "🎯 Розрахунок N+X",
        'calc_title_per_kg': "⚖️ Розрахунок ваги",
        'calc_title_original_price': "💼 Пошук ціни без знижки",
        'mode_pro_auto': "🌟 PRO: Авто-режим",
        'mode_pro_fixed': "🌟 PRO: Фікс. знижка",
        'mode_pro_loyal': "🌟 PRO: Картка лояльності",
        'mode_pro_double': "🌟 PRO: Подвійна знижка",
        'mode_pro_compare': "🌟 PRO: Порівняння товарів",
        'mode_pro_promo': "🌟 PRO: Порівняння промо",
        'mode_pro_margin': "🌟 PRO: Маржа",
        'mode_pro_history': "🌟 PRO: Історія",
        'pro_menu_title': "🌟 PRO режим. Оберіть функцію:",
        'pro_btn_auto': "🤖 Авто",
        'pro_btn_fixed': "💸 Фікс",
        'pro_btn_loyal': "💳 Картка",
        'pro_btn_double': "🔁 Подвійна",
        'pro_btn_compare': "⚖️ Порівняти",
        'pro_btn_promo': "📉 Промо",
        'pro_btn_margin': "📊 Маржа",
        'pro_btn_history': "📜 Історія",
        'pro_enter_expression': "✍️ Введіть вираз (299-40% або 2+1 ціна 60):",
        'pro_fixed_enter_price': "💰 Введіть ціну:",
        'pro_fixed_enter_discount_sum': "💸 Введіть суму знижки:",
        'pro_loyal_enter_regular': "💰 Ціна без картки:",
        'pro_loyal_enter_card': "💳 Ціна з карткою:",
        'pro_double_enter_price': "💰 Ціна товару:",
        'pro_double_enter_first': "🔁 Перша знижка (%):",
        'pro_double_enter_second': "🔁 Друга знижка (%):",
        'pro_compare_first_price': "1️⃣ Ціна товару 1:",
        'pro_compare_first_weight': "1️⃣ Вага товару 1:",
        'pro_compare_second_price': "2️⃣ Ціна товару 2:",
        'pro_compare_second_weight': "2️⃣ Вага товару 2:",
        'pro_promo_old_price': "💵 Стара ціна:",
        'pro_promo_new_price': "💸 Нова ціна:",
        'pro_margin_cost': "💼 Закупівля:",
        'pro_margin_shelf': "🏷️ Полиця:",
        'pro_history_empty': "Історія порожня.",
        'pro_history_title': "📜 Історія:",
        'pro_auto_unknown': "⚠️ Не зрозумів формат.",
        'discount_buttons': [
            [("5%", "5"), ("10%", "10"), ("15%", "15"), ("20%", "20")],
            [("25%", "25"), ("30%", "30"), ("35%", "35"), ("40%", "40")],
            [("45%", "45"), ("50%", "50"), ("Інший %", "інша_знижка")]
        ],
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
    """
    Отправляет сообщение, пытаясь подчистить старые (кроме клавиатуры).
    В версии с ReplyKeyboard мы не можем удалять сообщение пользователя с кнопкой,
    иначе он подумает, что бот глючит.
    """
    bot = context.bot
    chat_id = update.effective_chat.id

    # Удаляем старые сообщения бота, если они записаны
    old_ids = context.user_data.get("messages_to_delete", [])
    for mid in old_ids:
        try:
            await bot.delete_message(chat_id=chat_id, message_id=mid)
        except Exception:
            pass
    context.user_data["messages_to_delete"] = []

    # Отправляем новое сообщение
    sent = await bot.send_message(chat_id=chat_id, text=text, reply_markup=reply_markup)

    # Записываем ID нового сообщения, чтобы удалить его потом
    if not keep_result:
        context.user_data["messages_to_delete"].append(sent.message_id)

    return sent

def get_language_keyboard():
    # Для выбора языка используем Inline
    keyboard = [
        [InlineKeyboardButton("Русский", callback_data="lang_ru")],
        [InlineKeyboardButton("Українська", callback_data="lang_uk")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_main_menu_keyboard(context: ContextTypes.DEFAULT_TYPE):
    """
    Главное изменение: ReplyKeyboardMarkup (кнопки внизу).
    """
    lang = get_language(context)
    b = LOCALIZATION[lang]['buttons']
    keyboard = [
        [b['shelf'], b['nx']],
        [b['kg'], b['orig']],
        [b['pro'], b['settings']]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_discount_keyboard(context: ContextTypes.DEFAULT_TYPE):
    # Для выбора процентов оставляем Inline - это удобно
    lang = get_language(context)
    keyboard = [
        [InlineKeyboardButton(text, callback_data=data) for text, data in row]
        for row in LOCALIZATION[lang]['discount_buttons']
    ]
    # Добавляем кнопку "Назад" (хотя можно и через меню снизу выйти)
    # keyboard.append([InlineKeyboardButton(LOCALIZATION[lang]['back'], callback_data="назад")])
    return InlineKeyboardMarkup(keyboard)

def get_settings_keyboard(context: ContextTypes.DEFAULT_TYPE):
    lang = get_language(context)
    # Настройки - Inline
    keyboard = [
        [InlineKeyboardButton(LOCALIZATION[lang]['change_language'], callback_data="сменить_язык")],
    ]
    return InlineKeyboardMarkup(keyboard)

def get_pro_menu_keyboard(context: ContextTypes.DEFAULT_TYPE):
    lang = get_language(context)
    L = LOCALIZATION[lang]
    # PRO меню - Inline, так как функций много
    keyboard = [
        [InlineKeyboardButton(L['pro_btn_auto'], callback_data="pro_auto"), InlineKeyboardButton(L['pro_btn_fixed'], callback_data="pro_fixed")],
        [InlineKeyboardButton(L['pro_btn_loyal'], callback_data="pro_loyal"), InlineKeyboardButton(L['pro_btn_double'], callback_data="pro_double")],
        [InlineKeyboardButton(L['pro_btn_compare'], callback_data="pro_compare"), InlineKeyboardButton(L['pro_btn_promo'], callback_data="pro_promo")],
        [InlineKeyboardButton(L['pro_btn_margin'], callback_data="pro_margin"), InlineKeyboardButton(L['pro_btn_history'], callback_data="pro_history")],
    ]
    return InlineKeyboardMarkup(keyboard)

# ===== ОБРАБОТЧИКИ =====

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if 'language' not in context.user_data:
        context.user_data['попередній_стан'] = ВЫБОР_ЯЗЫКА
        await update.message.reply_text(
            "👋 Выберите язык / Оберіть мову:",
            reply_markup=get_language_keyboard()
        )
        return ВЫБОР_ЯЗЫКА

    lang = get_language(context)
    # Отправляем главное меню (кнопки снизу)
    await update.message.reply_text(
        LOCALIZATION[lang]['main_menu'],
        reply_markup=get_main_menu_keyboard(context),
        parse_mode="Markdown"
    )
    return ВЫБОР_ТИПА_СКИДКИ

async def restart(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data.clear()
    context.user_data['language'] = 'ru'
    await start(update, context)
    return ВЫБОР_ЯЗЫКА

async def choose_language(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    lang = query.data.split('_')[1]
    context.user_data['language'] = lang
    
    # После выбора языка показываем главное меню снизу
    await query.message.delete()
    await query.message.reply_text(
        LOCALIZATION[lang]['main_menu'],
        reply_markup=get_main_menu_keyboard(context),
        parse_mode="Markdown"
    )
    return ВЫБОР_ТИПА_СКИДКИ

async def settings_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    lang = get_language(context)
    # Настройки показываем сообщением с Inline кнопками
    await send_clean_message(
        update,
        context,
        LOCALIZATION[lang]['settings_menu'],
        reply_markup=get_settings_keyboard(context)
    )
    return НАСТРОЙКИ

async def change_language(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.callback_query.answer()
    await send_clean_message(
        update,
        context,
        "👋 Выберите язык / Оберіть мову:",
        reply_markup=get_language_keyboard()
    )
    return ВЫБОР_ЯЗЫКА

# --- ОСНОВНЫЕ ФУНКЦИИ (Обработчики нажатий на кнопки меню) ---

async def calculate_shelf_discount(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    lang = get_language(context)
    context.user_data['текущее_действие'] = 'menu_shelf_discount'
    
    # Теперь мы здесь, потому что нажали кнопку ТЕКСТОМ, а не Callback
    # Спрашиваем скидку (сразу показываем кнопки %)
    await send_clean_message(
        update,
        context,
        LOCALIZATION[lang]['select_discount'],
        reply_markup=get_discount_keyboard(context)
    )
    return ВЫБОР_ТИПА_СКИДКИ # Остаемся в этом состоянии, но уже ждем нажатия на %

async def handle_fixed_discount(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    # Обработка выбора процента (Inline кнопка)
    lang = get_language(context)
    await update.callback_query.answer()
    discount = float(update.callback_query.data)
    context.user_data['скидка'] = discount
    
    await send_clean_message(
        update,
        context,
        LOCALIZATION[lang]['enter_price'],
        reply_markup=None # Убираем кнопки, ждем текст
    )
    return ОЖИДАНИЕ_ЦЕНЫ

async def custom_discount(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    lang = get_language(context)
    await update.callback_query.answer()
    await send_clean_message(
        update,
        context,
        LOCALIZATION[lang]['enter_custom_discount'],
        reply_markup=None
    )
    return ОЖИДАНИЕ_СВОЕЙ_СКИДКИ

async def handle_discount_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    # Обработка ввода "своей" скидки руками
    lang = get_language(context)
    text = update.message.text.replace(',', '.')
    
    # Если юзер нажал кнопку меню, выходим
    if text in LOCALIZATION[lang]['buttons'].values():
        return await route_menu_button(update, context)

    try:
        discount = float(text)
        if not (0 < discount < 100): raise ValueError()
        context.user_data['скидка'] = discount
        await send_clean_message(update, context, LOCALIZATION[lang]['enter_price'])
        return ОЖИДАНИЕ_ЦЕНЫ
    except:
        await send_clean_message(update, context, LOCALIZATION[lang]['invalid_discount'])
        return ОЖИДАНИЕ_СВОЕЙ_СКИДКИ

async def handle_price_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    lang = get_language(context)
    text = update.message.text.replace(',', '.')

    # Проверка на выход в меню
    if text in LOCALIZATION[lang]['buttons'].values():
        return await route_menu_button(update, context)

    try:
        price = float(text)
        discount = context.user_data.get('скидка', 0)
        final = price * (1 - discount / 100)
        
        result_text = LOCALIZATION[lang]['price_result'].format(
            title=LOCALIZATION[lang]['calc_title_shelf'],
            price=price,
            discount=discount,
            extra="",
            discounted_price=final
        )
        
        # Показываем результат и снова ждем выбора скидки (цикл)
        await send_clean_message(update, context, result_text, keep_result=True)
        add_to_history(context, result_text)
        
        # Возвращаемся к выбору скидки, чтобы можно было посчитать другой товар
        await send_clean_message(
             update, 
             context, 
             LOCALIZATION[lang]['select_discount'], 
             reply_markup=get_discount_keyboard(context)
        )
        return ВЫБОР_ТИПА_СКИДКИ 
    except:
        await send_clean_message(update, context, LOCALIZATION[lang]['invalid_price'])
        return ОЖИДАНИЕ_ЦЕНЫ

# --- N+X ---

async def calculate_n_plus_x(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    lang = get_language(context)
    await send_clean_message(update, context, LOCALIZATION[lang]['enter_n'])
    return ОЖИДАНИЕ_N

async def handle_n_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    lang = get_language(context)
    text = update.message.text
    if text in LOCALIZATION[lang]['buttons'].values(): return await route_menu_button(update, context)
    
    if text.isdigit() and int(text) > 0:
        context.user_data['n'] = int(text)
        await send_clean_message(update, context, LOCALIZATION[lang]['enter_x'])
        return ОЖИДАНИЕ_X
    await send_clean_message(update, context, LOCALIZATION[lang]['invalid_number'])
    return ОЖИДАНИЕ_N

async def handle_x_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    lang = get_language(context)
    text = update.message.text
    if text in LOCALIZATION[lang]['buttons'].values(): return await route_menu_button(update, context)

    if text.isdigit() and int(text) > 0:
        context.user_data['x'] = int(text)
        await send_clean_message(update, context, LOCALIZATION[lang]['enter_nx_price'])
        return ОЖИДАНИЕ_ЦЕНЫ_NX
    await send_clean_message(update, context, LOCALIZATION[lang]['invalid_number'])
    return ОЖИДАНИЕ_X

async def handle_nx_price_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    lang = get_language(context)
    text = update.message.text.replace(',', '.')
    if text in LOCALIZATION[lang]['buttons'].values(): return await route_menu_button(update, context)

    try:
        price = float(text)
        n, x = context.user_data['n'], context.user_data['x']
        total_q = n + x
        total_sum = price * n
        unit_price = total_sum / total_q
        disc_perc = (x / total_q) * 100
        
        res = LOCALIZATION[lang]['nx_result'].format(
            title=LOCALIZATION[lang]['calc_title_nx'],
            n=n, x=x, price=price, total=total_sum, discount=disc_perc, unit_price=unit_price
        )
        await send_clean_message(update, context, res, keep_result=True)
        add_to_history(context, res)
        # Сразу предлагаем ввести N заново
        await send_clean_message(update, context, LOCALIZATION[lang]['enter_n'])
        return ОЖИДАНИЕ_N
    except:
        await send_clean_message(update, context, LOCALIZATION[lang]['invalid_price'])
        return ОЖИДАНИЕ_ЦЕНЫ_NX

# --- ВЕС ---

async def calculate_price_per_kg(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    lang = get_language(context)
    await send_clean_message(update, context, LOCALIZATION[lang]['enter_weight_price'])
    return ОЖИДАНИЕ_ЦЕНЫ_ВЕС

async def handle_weight_price_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    lang = get_language(context)
    text = update.message.text.replace(',', '.')
    if text in LOCALIZATION[lang]['buttons'].values(): return await route_menu_button(update, context)
    
    try:
        context.user_data['цена_веса'] = float(text)
        await send_clean_message(update, context, LOCALIZATION[lang]['enter_weight'])
        return ОЖИДАНИЕ_ГРАММОВ
    except:
        await send_clean_message(update, context, LOCALIZATION[lang]['invalid_price'])
        return ОЖИДАНИЕ_ЦЕНЫ_ВЕС

async def handle_weight_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    lang = get_language(context)
    text = update.message.text.replace(',', '.')
    if text in LOCALIZATION[lang]['buttons'].values(): return await route_menu_button(update, context)

    try:
        weight = float(text)
        price = context.user_data['цена_веса']
        kg_price = (price / weight) * 1000
        p100 = (price / weight) * 100
        
        res = LOCALIZATION[lang]['weight_result'].format(
            title=LOCALIZATION[lang]['calc_title_per_kg'],
            price=price, weight=weight, kg_price=kg_price, price_100g=p100
        )
        await send_clean_message(update, context, res, keep_result=True)
        add_to_history(context, res)
        # Цикл
        await send_clean_message(update, context, LOCALIZATION[lang]['enter_weight_price'])
        return ОЖИДАНИЕ_ЦЕНЫ_ВЕС
    except:
        await send_clean_message(update, context, LOCALIZATION[lang]['invalid_number'])
        return ОЖИДАНИЕ_ГРАММОВ

# --- Original Price ---

async def calculate_original_price(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    lang = get_language(context)
    await send_clean_message(update, context, LOCALIZATION[lang]['enter_price'])
    return ОЖИДАНИЕ_ЦЕНЫ_СО_СКИДКОЙ

async def handle_discounted_price(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    lang = get_language(context)
    text = update.message.text.replace(',', '.')
    if text in LOCALIZATION[lang]['buttons'].values(): return await route_menu_button(update, context)

    try:
        context.user_data['цена_со_скидкой'] = float(text)
        await send_clean_message(update, context, LOCALIZATION[lang]['enter_custom_discount'])
        return ОЖИДАНИЕ_ПРОЦЕНТА_СКИДКИ
    except:
        await send_clean_message(update, context, LOCALIZATION[lang]['invalid_price'])
        return ОЖИДАНИЕ_ЦЕНЫ_СО_СКИДКОЙ

async def calculate_original_price_result(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    lang = get_language(context)
    text = update.message.text.replace(',', '.')
    if text in LOCALIZATION[lang]['buttons'].values(): return await route_menu_button(update, context)

    try:
        disc = float(text)
        final = context.user_data['цена_со_скидкой']
        orig = final / (1 - disc / 100)
        
        # Используем существующий шаблон price_result для красоты
        res = LOCALIZATION[lang]['price_result'].format(
            title=LOCALIZATION[lang]['calc_title_original_price'],
            price=orig, discount=disc, extra=" (восстановленная)", discounted_price=final
        )
        await send_clean_message(update, context, res, keep_result=True)
        add_to_history(context, res)
        await send_clean_message(update, context, LOCALIZATION[lang]['enter_price'])
        return ОЖИДАНИЕ_ЦЕНЫ_СО_СКИДКОЙ
    except:
        await send_clean_message(update, context, LOCALIZATION[lang]['invalid_discount'])
        return ОЖИДАНИЕ_ПРОЦЕНТА_СКИДКИ

# --- PRO MENU (Inline) ---

async def open_pro_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    lang = get_language(context)
    # Показываем PRO меню как Inline (так как там много опций)
    await send_clean_message(
        update,
        context,
        LOCALIZATION[lang]['pro_menu_title'],
        reply_markup=get_pro_menu_keyboard(context)
    )
    return PRO_MENU

async def pro_callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    # Заглушка для обработки кнопок PRO (чтобы код не был бесконечным)
    # Вы можете добавить сюда логику из предыдущих версий для PRO
    await update.callback_query.answer()
    await update.callback_query.message.reply_text("Функция PRO выбрана (добавьте логику)")
    return PRO_MENU

# --- ГЛАВНЫЙ МАРШРУТИЗАТОР МЕНЮ ---
# Эта функция проверяет, какую кнопку нажал пользователь в нижнем меню

async def route_menu_button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    text = update.message.text
    lang = get_language(context)
    b = LOCALIZATION[lang]['buttons']
    
    if text == b['shelf']:
        return await calculate_shelf_discount(update, context)
    elif text == b['nx']:
        return await calculate_n_plus_x(update, context)
    elif text == b['kg']:
        return await calculate_price_per_kg(update, context)
    elif text == b['orig']:
        return await calculate_original_price(update, context)
    elif text == b['pro']:
        return await open_pro_menu(update, context)
    elif text == b['settings']:
        return await settings_menu(update, context)
    elif text == b['restart']:
        return await restart(update, context)
    
    # Если текст не кнопка - игнорируем или просим нажать кнопку
    await update.message.reply_text(LOCALIZATION[lang]['unexpected_text'])
    return ВЫБОР_ТИПА_СКИДКИ

# ===== ЗАПУСК =====

def get_application():
    if not TOKEN:
        raise ValueError("Токен не найден!")
    app = ApplicationBuilder().token(TOKEN).build()
    
    # Регулярки для кнопок меню (чтобы ловить их в любом состоянии)
    # Мы собираем все названия кнопок на обоих языках
    menu_buttons = []
    for l in LOCALIZATION.values():
        menu_buttons.extend(l['buttons'].values())
    menu_filter = filters.Regex(f"^({'|'.join(map(re.escape, menu_buttons))})$")

    # В любом состоянии диалога, если нажата кнопка меню -> идем в route_menu_button
    # Это делается через entry_points (если мы в начале) или через fallbacks (если мы внутри процесса)
    
    conv_handler = ConversationHandler(
        entry_points=[
            CommandHandler("start", start),
            MessageHandler(menu_filter, route_menu_button)
        ],
        states={
            ВЫБОР_ЯЗЫКА: [CallbackQueryHandler(choose_language, pattern="^lang_")],
            
            # Главное состояние ожидания
            ВЫБОР_ТИПА_СКИДКИ: [
                MessageHandler(menu_filter, route_menu_button),
                # Если нажали Inline кнопку процента (когда мы в режиме скидок)
                CallbackQueryHandler(handle_fixed_discount, pattern="^(5|10|15|20|25|30|35|40|45|50)$"),
                CallbackQueryHandler(custom_discount, pattern="^другая_скидка$"),
                # PRO
                CallbackQueryHandler(pro_callback_handler, pattern="^pro_"),
            ],
            
            # Состояния ввода данных
            # В каждом из них мы сначала проверяем menu_filter (вдруг юзер передумал и нажал другую кнопку)
            ОЖИДАНИЕ_ЦЕНЫ: [MessageHandler(menu_filter, route_menu_button), MessageHandler(filters.TEXT, handle_price_input)],
            ОЖИДАНИЕ_СВОЕЙ_СКИДКИ: [MessageHandler(menu_filter, route_menu_button), MessageHandler(filters.TEXT, handle_discount_input)],
            
            # N+X
            ОЖИДАНИЕ_N: [MessageHandler(menu_filter, route_menu_button), MessageHandler(filters.TEXT, handle_n_input)],
            ОЖИДАНИЕ_X: [MessageHandler(menu_filter, route_menu_button), MessageHandler(filters.TEXT, handle_x_input)],
            ОЖИДАНИЕ_ЦЕНЫ_NX: [MessageHandler(menu_filter, route_menu_button), MessageHandler(filters.TEXT, handle_nx_price_input)],
            
            # Вес
            ОЖИДАНИЕ_ЦЕНЫ_ВЕС: [MessageHandler(menu_filter, route_menu_button), MessageHandler(filters.TEXT, handle_weight_price_input)],
            ОЖИДАНИЕ_ГРАММОВ: [MessageHandler(menu_filter, route_menu_button), MessageHandler(filters.TEXT, handle_weight_input)],
            
            # Orig
            ОЖИДАНИЕ_ЦЕНЫ_СО_СКИДКОЙ: [MessageHandler(menu_filter, route_menu_button), MessageHandler(filters.TEXT, handle_discounted_price)],
            ОЖИДАНИЕ_ПРОЦЕНТА_СКИДКИ: [MessageHandler(menu_filter, route_menu_button), MessageHandler(filters.TEXT, calculate_original_price_result)],

            # Settings
            НАСТРОЙКИ: [CallbackQueryHandler(change_language, pattern="^сменить_язык$"), MessageHandler(menu_filter, route_menu_button)],
            
            # PRO (меню)
            PRO_MENU: [CallbackQueryHandler(pro_callback_handler, pattern="^pro_"), MessageHandler(menu_filter, route_menu_button)],
        },
        fallbacks=[CommandHandler("start", restart)],
        per_chat=True
    )
    
    app.add_handler(conv_handler)
    return app

# Алиас
register_handlers = get_application
