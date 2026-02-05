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

TOKEN = os.getenv("TOKEN")

# Логирование
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# --- КОНСТАНТЫ И МЕНЮ ---

# Состояния (упрощаем, нам нужно меньше состояний благодаря умному вводу)
(
    MAIN_STATE,  # Главное состояние, где бот слушает любой ввод
    SETTINGS,    # Настройки языка
) = range(2)

# Тексты (короткие и ясные)
LOCALIZATION = {
    'ru': {
        'menu_shelf': "🏷 % Скидка",
        'menu_kg': "⚖️ Цена за кг",
        'menu_nx': "🎁 Акция N+X",
        'menu_settings': "⚙️ Язык",
        'start': "👇 Выберите режим внизу или просто напишите числа:\n\n• **299** → спрошу скидку\n• **299 40** → цена 299, скидка 40%\n• **120 400** → 120 грн за 400 г",
        'ask_discount': "💰 Цена: **{price}** грн.\nВыберите скидку или введите свою:",
        'ask_price_kg': "⚖️ Режим **Цена за КГ**.\nВведите: `Цена Вес` (например: `150 300`)",
        'ask_nx': "🎁 Режим **N+X**.\nВведите: `N X Цена` (например: `2 1 49.99`)\nГде 2+1 — акция, 49.99 — цена шт.",
        'res_shelf': "🏷 **{price}** -{disc}% = **{total}** грн\n🔻 Экономия: {diff} грн",
        'res_kg': "⚖️ {weight}г = {price} грн\n📊 **1 кг = {kg_price} грн**",
        'res_nx': "🎁 {n}+{x} по {price} грн\n🛒 Всего: {sum} грн\n📉 Скидка: {disc:.1f}%\n✅ **1 шт = {unit} грн**",
        'err_num': "🤷‍♂️ Не понял числа. Попробуйте еще раз.",
        'lang_sel': "Выберите язык:",
        'saved': "✅ Сохранено"
    },
    'uk': {
        'menu_shelf': "🏷 % Знижка",
        'menu_kg': "⚖️ Ціна за кг",
        'menu_nx': "🎁 Акція N+X",
        'menu_settings': "⚙️ Мова",
        'start': "👇 Оберіть режим знизу або просто напишіть числа:\n\n• **299** → запитаю знижку\n• **299 40** → ціна 299, знижка 40%\n• **120 400** → 120 грн за 400 г",
        'ask_discount': "💰 Ціна: **{price}** грн.\nОберіть знижку або введіть свою:",
        'ask_price_kg': "⚖️ Режим **Ціна за КГ**.\nВведіть: `Ціна Вага` (наприклад: `150 300`)",
        'ask_nx': "🎁 Режим **N+X**.\nВведіть: `N X Ціна` (наприклад: `2 1 49.99`)\nДе 2+1 — акція, 49.99 — ціна шт.",
        'res_shelf': "🏷 **{price}** -{disc}% = **{total}** грн\n🔻 Економія: {diff} грн",
        'res_kg': "⚖️ {weight}г = {price} грн\n📊 **1 кг = {kg_price} грн**",
        'res_nx': "🎁 {n}+{x} по {price} грн\n🛒 Загалом: {sum} грн\n📉 Знижка: {disc:.1f}%\n✅ **1 шт = {unit} грн**",
        'err_num': "🤷‍♂️ Не зрозумів числа. Спробуйте ще раз.",
        'lang_sel': "Оберіть мову:",
        'saved': "✅ Збережено"
    }
}

# --- КЛАВИАТУРЫ ---

def get_lang(context):
    return context.user_data.get('lang', 'ru')

def get_main_keyboard(lang_code):
    l = LOCALIZATION[lang_code]
    # Постоянная клавиатура внизу (ReplyKeyboard)
    return ReplyKeyboardMarkup(
        [[l['menu_shelf'], l['menu_kg']], [l['menu_nx'], l['menu_settings']]],
        resize_keyboard=True
    )

def get_discount_inline_kb():
    # Кнопки для быстрого выбора скидки
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("-5%", callback_data="d_5"), InlineKeyboardButton("-10%", callback_data="d_10"), InlineKeyboardButton("-15%", callback_data="d_15")],
        [InlineKeyboardButton("-20%", callback_data="d_20"), InlineKeyboardButton("-25%", callback_data="d_25"), InlineKeyboardButton("-30%", callback_data="d_30")],
        [InlineKeyboardButton("-35%", callback_data="d_35"), InlineKeyboardButton("-40%", callback_data="d_40"), InlineKeyboardButton("-50%", callback_data="d_50")],
        [InlineKeyboardButton("-60%", callback_data="d_60"), InlineKeyboardButton("-70%", callback_data="d_70"), InlineKeyboardButton("-75%", callback_data="d_75")],
    ])

def get_lang_kb():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("Русский", callback_data="set_ru"), InlineKeyboardButton("Українська", callback_data="set_uk")]
    ])

# --- ЛОГИКА ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = get_lang(context)
    # Очищаем контекст при рестарте, но сохраняем язык
    context.user_data.clear()
    context.user_data['lang'] = lang
    
    await update.message.reply_text(
        LOCALIZATION[lang]['start'],
        parse_mode='Markdown',
        reply_markup=get_main_keyboard(lang)
    )
    return MAIN_STATE

async def handle_text_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip().replace(',', '.')
    lang = get_lang(context)
    l = LOCALIZATION[lang]

    # 1. Проверка на нажатие кнопок меню
    if text == l['menu_shelf']:
        context.user_data['mode'] = 'shelf'
        await update.message.reply_text("👇 Введите цену товара:", reply_markup=get_main_keyboard(lang))
        return MAIN_STATE
    elif text == l['menu_kg']:
        context.user_data['mode'] = 'kg'
        await update.message.reply_text(l['ask_price_kg'], parse_mode='Markdown', reply_markup=get_main_keyboard(lang))
        return MAIN_STATE
    elif text == l['menu_nx']:
        context.user_data['mode'] = 'nx'
        await update.message.reply_text(l['ask_nx'], parse_mode='Markdown', reply_markup=get_main_keyboard(lang))
        return MAIN_STATE
    elif text == l['menu_settings']:
        await update.message.reply_text(l['lang_sel'], reply_markup=get_lang_kb())
        return SETTINGS

    # 2. Умный парсинг чисел (Smart Input)
    # Пытаемся найти все числа в сообщении
    nums = [float(x) for x in re.findall(r'-?\d+(?:\.\d+)?', text)]

    if not nums:
        await update.message.reply_text(l['err_num'])
        return MAIN_STATE

    # СЦЕНАРИЙ А: Одно число (обычно это Цена)
    if len(nums) == 1:
        price = nums[0]
        # Если мы в режиме "Скидка" (или по умолчанию), считаем это ценой и просим скидку
        context.user_data['temp_price'] = price
        await update.message.reply_text(
            l['ask_discount'].format(price=price),
            parse_mode='Markdown',
            reply_markup=get_discount_inline_kb()
        )
        return MAIN_STATE

    # СЦЕНАРИЙ Б: Два числа
    if len(nums) == 2:
        val1, val2 = nums[0], nums[1]
        
        # Если активен режим КГ
        if context.user_data.get('mode') == 'kg':
             # Обычно сначала пишут цену, потом вес, или наоборот. 
             # Эвристика: вес обычно > цены (в граммах), но не всегда.
             # Допустим жесткий формат: Цена пробел Вес(г)
            price, weight = val1, val2
            kg_price = (price / weight) * 1000
            await update.message.reply_text(
                l['res_kg'].format(weight=weight, price=price, kg_price=f"{kg_price:.2f}"),
                parse_mode='Markdown'
            )
            return MAIN_STATE

        # Иначе считаем это СКИДКОЙ (Цена Процент)
        # Например: 200 20 -> 200 грн - 20%
        # Или: 200 -20
        price = val1
        disc = abs(val2) # убираем минус если пользователь написал "200 -20"
        
        if disc >= 100:
             # Скорее всего это не скидка, а вес (человек забыл переключить режим)
             # Посчитаем как вес на всякий случай
             weight = disc
             kg_price = (price / weight) * 1000
             await update.message.reply_text(
                f"🤔 Скидка {disc}% великовата. Посчитал как вес:\n" + 
                l['res_kg'].format(weight=weight, price=price, kg_price=f"{kg_price:.2f}"),
                parse_mode='Markdown'
            )
             return MAIN_STATE

        final = price * (1 - disc/100)
        diff = price - final
        await update.message.reply_text(
            l['res_shelf'].format(price=price, disc=disc, total=f"{final:.2f}", diff=f"{diff:.2f}"),
            parse_mode='Markdown'
        )
        return MAIN_STATE

    # СЦЕНАРИЙ В: Три числа (N + X + Цена)
    if len(nums) == 3:
        n, x, price = int(nums[0]), int(nums[1]), nums[2]
        total_q = n + x
        total_sum = price * n
        unit_price = total_sum / total_q
        real_disc = (x / total_q) * 100
        
        await update.message.reply_text(
            l['res_nx'].format(n=n, x=x, price=price, sum=f"{total_sum:.2f}", disc=real_disc, unit=f"{unit_price:.2f}"),
            parse_mode='Markdown'
        )
        return MAIN_STATE

    return MAIN_STATE

async def handle_inline_discount(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    lang = get_lang(context)
    l = LOCALIZATION[lang]
    
    # Получаем скидку из нажатой кнопки (d_20 -> 20)
    disc = float(query.data.split('_')[1])
    price = context.user_data.get('temp_price')

    if not price:
        await query.message.reply_text("⚠️ Цена потерялась. Введите её заново.")
        return MAIN_STATE

    final = price * (1 - disc/100)
    diff = price - final
    
    # Редактируем сообщение с кнопками, превращая его в результат
    await query.message.edit_text(
        l['res_shelf'].format(price=price, disc=disc, total=f"{final:.2f}", diff=f"{diff:.2f}"),
        parse_mode='Markdown'
    )
    return MAIN_STATE

async def handle_language_setting(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    lang_code = query.data.split('_')[1] # set_ru -> ru
    context.user_data['lang'] = lang_code
    
    # Обновляем клавиатуру под новый язык
    await query.message.delete()
    await query.message.reply_text(
        LOCALIZATION[lang_code]['saved'],
        reply_markup=get_main_keyboard(lang_code)
    )
    return MAIN_STATE

# ===== ЗАПУСК =====

def get_application():
    if not TOKEN:
        raise ValueError("Токен не найден! Проверь переменные окружения.")
    
    app = ApplicationBuilder().token(TOKEN).build()
    
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start), MessageHandler(filters.TEXT, handle_text_input)],
        states={
            MAIN_STATE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text_input),
                CallbackQueryHandler(handle_inline_discount, pattern="^d_"),
            ],
            SETTINGS: [
                CallbackQueryHandler(handle_language_setting, pattern="^set_")
            ]
        },
        fallbacks=[CommandHandler("start", start)],
        per_chat=True
    )
    
    app.add_handler(conv_handler)
    return app
