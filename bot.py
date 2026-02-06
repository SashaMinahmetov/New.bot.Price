diff --git a/bot.py b/bot.py
index 2de7642bef64fc95339c21e56ffa144990882507..e6d90404769c47b1559f8e03fecfb924fd7c908f 100644
--- a/bot.py
+++ b/bot.py
@@ -42,53 +42,53 @@ TOKEN = os.getenv("TOKEN")
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
 
 # Словари с локализацией
 LOCALIZATION = {
-    'ru': {
-        'welcome': "👋 Добро пожаловать! Выберите язык:",
-        'main_menu': "👋 Добро пожаловать! Выберите опцию для расчета:",
+    'ru': {
+        'welcome': "👋 Добро пожаловать! Выберите язык:",
+        'main_menu': "👋 Добро пожаловать! Выберите опцию для расчета:\n\n✨ Напоминание: у нас есть удобное mini app — можете открыть его из меню Telegram.",
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
@@ -129,53 +129,53 @@ LOCALIZATION = {
         'pro_btn_compare': "⚖️ Сравнить 2 товара",
         'pro_btn_promo': "📉 Сравнить промо и обычную цену",
         'pro_btn_margin': "📊 Маржа и наценка",
         'pro_btn_history': "📜 История расчётов",
         'pro_enter_expression': "✍️ Отправьте выражение одним сообщением.\nПримеры:\n• 299 - 40%\n• 2+1 цена 60\n• 350 г за 42",
         'pro_fixed_enter_price': "💰 Введите цену товара:",
         'pro_fixed_enter_discount_sum': "💸 Введите размер скидки в гривнах:",
         'pro_loyal_enter_regular': "💰 Введите обычную цену (без карты):",
         'pro_loyal_enter_card': "💳 Введите цену по карте лояльности:",
         'pro_double_enter_price': "💰 Введите цену товара:",
         'pro_double_enter_first': "🔁 Введите первую скидку в процентах:",
         'pro_double_enter_second': "🔁 Введите вторую скидку в процентах:",
         'pro_compare_first_price': "1️⃣ Введите цену первого товара:",
         'pro_compare_first_weight': "1️⃣ Введите вес/объем первого товара (в граммах или мл):",
         'pro_compare_second_price': "2️⃣ Введите цену второго товара:",
         'pro_compare_second_weight': "2️⃣ Введите вес/объем второго товара (в граммах или мл):",
         'pro_promo_old_price': "💵 Введите обычную цену (до скидки):",
         'pro_promo_new_price': "💸 Введите акционную цену (со скидкой):",
         'pro_margin_cost': "💼 Введите закупочную цену товара:",
         'pro_margin_shelf': "🏷️ Введите цену товара на полке:",
         'pro_history_empty': "Пока нет сохранённых расчётов.",
         'pro_history_title': "📜 История последних расчётов:",
         'pro_invalid_number': "❌ Некорректное значение. Введите число, например 123.45",
         'pro_auto_unknown': "⚠️ Не удалось распознать выражение.\nПопробуйте другой формат или используйте стандартные режимы.",
     },
-    'uk': {
-        'welcome': "👋 Ласкаво просимо! Оберіть мову:",
-        'main_menu': "👋 Ласкаво просимо! Оберіть опцію для розрахунку:",
+    'uk': {
+        'welcome': "👋 Ласкаво просимо! Оберіть мову:",
+        'main_menu': "👋 Ласкаво просимо! Оберіть опцію для розрахунку:\n\n✨ Нагадування: у нас є зручний mini app — можете відкрити його з меню Telegram.",
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
@@ -342,59 +342,81 @@ def get_next_actions_keyboard(context: ContextTypes.DEFAULT_TYPE):
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
 
 
-def get_numeric_reply_keyboard():
+def get_numeric_reply_keyboard():
     keyboard = [
         ["1", "2", "3"],
         ["4", "5", "6"],
         ["7", "8", "9"],
         ["10"],
     ]
-    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
-
+    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
+
+def parse_positive_float(text: str):
+    try:
+        value = float(text.replace(',', '.').strip())
+    except (ValueError, AttributeError):
+        return None
+    return value if value > 0 else None
+
+async def prompt_n_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
+    lang = get_language(context)
+    await send_clean_message(update, context, LOCALIZATION[lang]['enter_n'], reply_markup=get_numeric_reply_keyboard())
+    return ОЖИДАНИЕ_N
+
+async def prompt_x_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
+    lang = get_language(context)
+    await send_clean_message(update, context, LOCALIZATION[lang]['enter_x'], reply_markup=get_numeric_reply_keyboard())
+    return ОЖИДАНИЕ_X
+
+async def prompt_discount_percent(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
+    lang = get_language(context)
+    await send_clean_message(update, context, LOCALIZATION[lang]['enter_custom_discount'], reply_markup=None)
+    return ОЖИДАНИЕ_ПРОЦЕНТА_СКИДКИ
+
 
 def get_pro_menu_keyboard(context: ContextTypes.DEFAULT_TYPE):
     lang = get_language(context)
     L = LOCALIZATION[lang]
     keyboard = [
         [InlineKeyboardButton(L['pro_btn_auto'], callback_data="pro_auto")],
         [InlineKeyboardButton(L['pro_btn_fixed'], callback_data="pro_fixed")],
         [InlineKeyboardButton(L['pro_btn_loyal'], callback_data="pro_loyal")],
         [InlineKeyboardButton(L['pro_btn_double'], callback_data="pro_double")],
         [InlineKeyboardButton(L['pro_btn_compare'], callback_data="pro_compare")],
         [InlineKeyboardButton(L['pro_btn_promo'], callback_data="pro_promo")],
         [InlineKeyboardButton(L['pro_btn_margin'], callback_data="pro_margin")],
         [InlineKeyboardButton(L['pro_btn_history'], callback_data="pro_history")],
         [InlineKeyboardButton(L['back'], callback_data="назад")],
         [InlineKeyboardButton(LOCALIZATION[lang]['restart_btn'], callback_data="перезапустить_бот")],
     ]
     return InlineKeyboardMarkup(keyboard)
 
 # ===== ОБРАБОТЧИКИ =====
 
 async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
     if 'language' not in context.user_data:
         context.user_data['попередній_стан'] = ВЫБОР_ЯЗЫКА
         await send_clean_message(
             update,
@@ -610,80 +632,79 @@ async def calculate_n_plus_x(update: Update, context: ContextTypes.DEFAULT_TYPE)
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
 
 
-async def handle_n_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
-    lang = get_language(context)
-    text = update.message.text.strip()
+async def handle_n_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
+    lang = get_language(context)
+    text = update.message.text.strip()
     if not text.isdigit():
         await send_clean_message(update, context, LOCALIZATION[lang]['invalid_number'], reply_markup=get_numeric_reply_keyboard())
         return ОЖИДАНИЕ_N
     n = int(text)
     if n <= 0:
         await send_clean_message(update, context, LOCALIZATION[lang]['invalid_number'], reply_markup=get_numeric_reply_keyboard())
         return ОЖИДАНИЕ_N
-    context.user_data['n'] = n
-    context.user_data['попередній_стан'] = ОЖИДАНИЕ_N
-    await send_clean_message(update, context, LOCALIZATION[lang]['enter_x'], reply_markup=get_numeric_reply_keyboard())
-    return ОЖИДАНИЕ_X
+    context.user_data['n'] = n
+    context.user_data['попередній_стан'] = ОЖИДАНИЕ_N
+    return await prompt_x_input(update, context)
 
 
-async def handle_x_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
-    lang = get_language(context)
-    text = update.message.text.strip()
+async def handle_x_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
+    lang = get_language(context)
+    text = update.message.text.strip()
     if not text.isdigit():
         await send_clean_message(update, context, LOCALIZATION[lang]['invalid_number'], reply_markup=get_numeric_reply_keyboard())
         return ОЖИДАНИЕ_X
     x = int(text)
     if x <= 0:
         await send_clean_message(update, context, LOCALIZATION[lang]['invalid_number'], reply_markup=get_numeric_reply_keyboard())
         return ОЖИДАНИЕ_X
-    context.user_data['x'] = x
-    context.user_data['попередній_стан'] = ОЖИДАНИЕ_X
-    await send_clean_message(update, context, LOCALIZATION[lang]['enter_nx_price'], reply_markup=ReplyKeyboardRemove())
-    return ОЖИДАНИЕ_ЦЕНЫ_NX
+    context.user_data['x'] = x
+    context.user_data['попередній_стан'] = ОЖИДАНИЕ_X
+    await send_clean_message(update, context, LOCALIZATION[lang]['enter_nx_price'], reply_markup=ReplyKeyboardRemove())
+    return ОЖИДАНИЕ_ЦЕНЫ_NX
 
 
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
@@ -749,65 +770,59 @@ async def handle_weight_input(update: Update, context: ContextTypes.DEFAULT_TYPE
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
 
 
-async def handle_discounted_price(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
-    lang = get_language(context)
-    text = update.message.text.replace(',', '.')
-    try:
-        price = float(text)
-        if price <= 0:
-            await send_clean_message(update, context, LOCALIZATION[lang]['invalid_price'])
-            return ОЖИДАНИЕ_ЦЕНЫ_СО_СКИДКОЙ
-        context.user_data['цена_со_скидкой'] = price
-        context.user_data['попередній_стан'] = ОЖИДАНИЕ_ЦЕНЫ_СО_СКИДКОЙ
-        await send_clean_message(update, context, LOCALIZATION[lang]['enter_custom_discount'], reply_markup=None)
-        return ОЖИДАНИЕ_ПРОЦЕНТА_СКИДКИ
-    except ValueError:
-        await send_clean_message(update, context, LOCALIZATION[lang]['invalid_price'])
-        return ОЖИДАНИЕ_ЦЕНЫ_СО_СКИДКОЙ
+async def handle_discounted_price(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
+    lang = get_language(context)
+    price = parse_positive_float(update.message.text)
+    if price is None:
+        await send_clean_message(update, context, LOCALIZATION[lang]['invalid_price'])
+        return ОЖИДАНИЕ_ЦЕНЫ_СО_СКИДКОЙ
+    context.user_data['цена_со_скидкой'] = price
+    context.user_data['попередній_стан'] = ОЖИДАНИЕ_ЦЕНЫ_СО_СКИДКОЙ
+    return await prompt_discount_percent(update, context)
 
 
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
 
@@ -859,262 +874,299 @@ async def pro_handle_automode(update: Update, context: ContextTypes.DEFAULT_TYPE
     if parsed['type'] == 'percent':
         res = f"🤖 Авто: {parsed['price']} - {parsed['discount']}%\n✅ {parsed['price']*(1-parsed['discount']/100):.2f} грн"
     elif parsed['type'] == 'nx':
         n, x, p = parsed['n'], parsed['x'], parsed['price']
         res = f"🤖 Авто: {n}+{x}\n✅ Единица: {p*n/(n+x):.2f} грн (Всего: {p*n:.2f})"
     elif parsed['type'] == 'per_kg':
         w, p = parsed['weight'], parsed['price']
         res = f"🤖 Авто: вес\n✅ 1 кг: {(p/w)*1000:.2f} грн"
     await send_clean_message(update, context, res, reply_markup=None, keep_result=True)
     add_to_history(context, res)
     await send_clean_message(update, context, LOCALIZATION[lang]['next_action_prompt'], reply_markup=get_next_actions_keyboard(context))
     return ВЫБОР_ТИПА_СКИДКИ
 
 # --- PRO Handlers (Fixed, Loyal, Double, Compare, Promo, Margin, History) ---
 # Для краткости приведены стартеры и обработчики
 
 async def pro_fixed_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
     lang = get_language(context)
     if update.callback_query: await update.callback_query.answer()
     context.user_data['попередній_стан'] = PRO_MENU
     mode_msg = await send_clean_message(update, context, LOCALIZATION[lang]['mode_pro_fixed'], reply_markup=None, keep_result=True)
     context.user_data['mode_message_id'] = mode_msg.message_id
     await send_clean_message(update, context, LOCALIZATION[lang]['pro_fixed_enter_price'], reply_markup=None)
     return PRO_FIXED_PRICE
 
-async def pro_fixed_price_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
-    try:
-        context.user_data['pro_fixed_price'] = float(update.message.text.replace(',', '.'))
-        await send_clean_message(update, context, LOCALIZATION[get_language(context)]['pro_fixed_enter_discount_sum'])
-        return PRO_FIXED_DISCOUNT
-    except:
-        await send_clean_message(update, context, LOCALIZATION[get_language(context)]['pro_invalid_number'])
-        return PRO_FIX_PRICE
-
-async def pro_fixed_discount_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
-    try:
-        disc = float(update.message.text.replace(',', '.'))
-        price = context.user_data.get('pro_fixed_price')
-        await delete_mode_message(update, context)
-        res = f"💸 Фикс. скидка\n💰 Цена: {price}\n⬇️ Скидка: {disc}\n✅ Итог: {price-disc:.2f} грн"
-        await send_clean_message(update, context, res, keep_result=True)
-        add_to_history(context, res)
-        await send_clean_message(update, context, LOCALIZATION[get_language(context)]['next_action_prompt'], reply_markup=get_next_actions_keyboard(context))
-        return ВЫБОР_ТИПА_СКИДКИ
-    except: return PRO_FIXED_DISCOUNT
+async def pro_fixed_price_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
+    price = parse_positive_float(update.message.text)
+    if price is None:
+        await send_clean_message(update, context, LOCALIZATION[get_language(context)]['pro_invalid_number'])
+        return PRO_FIXED_PRICE
+    context.user_data['pro_fixed_price'] = price
+    await send_clean_message(update, context, LOCALIZATION[get_language(context)]['pro_fixed_enter_discount_sum'])
+    return PRO_FIXED_DISCOUNT
+
+async def pro_fixed_discount_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
+    disc = parse_positive_float(update.message.text)
+    price = context.user_data.get('pro_fixed_price')
+    if disc is None or price is None:
+        await send_clean_message(update, context, LOCALIZATION[get_language(context)]['pro_invalid_number'])
+        return PRO_FIXED_DISCOUNT
+    await delete_mode_message(update, context)
+    res = f"💸 Фикс. скидка\n💰 Цена: {price}\n⬇️ Скидка: {disc}\n✅ Итог: {price-disc:.2f} грн"
+    await send_clean_message(update, context, res, keep_result=True)
+    add_to_history(context, res)
+    await send_clean_message(update, context, LOCALIZATION[get_language(context)]['next_action_prompt'], reply_markup=get_next_actions_keyboard(context))
+    return ВЫБОР_ТИПА_СКИДКИ
 
 async def pro_loyal_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
     if update.callback_query: await update.callback_query.answer()
     context.user_data['попередній_стан'] = PRO_MENU
     await send_clean_message(update, context, LOCALIZATION[get_language(context)]['pro_loyal_enter_regular'])
     return PRO_LOYAL_ORIGINAL
 
-async def pro_loyal_original_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
-    try:
-        context.user_data['pro_loyal_original'] = float(update.message.text.replace(',', '.'))
-        await send_clean_message(update, context, LOCALIZATION[get_language(context)]['pro_loyal_enter_card'])
-        return PRO_LOYAL_CARD
-    except: return PRO_LOYAL_ORIGINAL
-
-async def pro_loyal_card_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
-    try:
-        card = float(update.message.text.replace(',', '.'))
-        orig = context.user_data.get('pro_loyal_original')
-        res = f"💳 Карта\n💰 Без: {orig}\n💳 С картой: {card}\n⬇️ Выгода: {orig-card:.2f}"
-        await send_clean_message(update, context, res, keep_result=True)
-        add_to_history(context, res)
-        await send_clean_message(update, context, LOCALIZATION[get_language(context)]['next_action_prompt'], reply_markup=get_next_actions_keyboard(context))
-        return ВЫБОР_ТИПА_СКИДКИ
-    except: return PRO_LOYAL_CARD
+async def pro_loyal_original_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
+    orig = parse_positive_float(update.message.text)
+    if orig is None:
+        await send_clean_message(update, context, LOCALIZATION[get_language(context)]['pro_invalid_number'])
+        return PRO_LOYAL_ORIGINAL
+    context.user_data['pro_loyal_original'] = orig
+    await send_clean_message(update, context, LOCALIZATION[get_language(context)]['pro_loyal_enter_card'])
+    return PRO_LOYAL_CARD
+
+async def pro_loyal_card_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
+    card = parse_positive_float(update.message.text)
+    orig = context.user_data.get('pro_loyal_original')
+    if card is None or orig is None:
+        await send_clean_message(update, context, LOCALIZATION[get_language(context)]['pro_invalid_number'])
+        return PRO_LOYAL_CARD
+    res = f"💳 Карта\n💰 Без: {orig}\n💳 С картой: {card}\n⬇️ Выгода: {orig-card:.2f}"
+    await send_clean_message(update, context, res, keep_result=True)
+    add_to_history(context, res)
+    await send_clean_message(update, context, LOCALIZATION[get_language(context)]['next_action_prompt'], reply_markup=get_next_actions_keyboard(context))
+    return ВЫБОР_ТИПА_СКИДКИ
 
 async def pro_double_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
     if update.callback_query: await update.callback_query.answer()
     context.user_data['попередній_стан'] = PRO_MENU
     await send_clean_message(update, context, LOCALIZATION[get_language(context)]['pro_double_enter_price'])
     return PRO_DOUBLE_PRICE
 
-async def pro_double_price_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
-    try:
-        context.user_data['pro_double_price'] = float(update.message.text.replace(',', '.'))
-        await send_clean_message(update, context, LOCALIZATION[get_language(context)]['pro_double_enter_first'])
-        return PRO_DOUBLE_DISC1
-    except: return PRO_DOUBLE_PRICE
-
-async def pro_double_disc1_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
-    try:
-        context.user_data['pro_double_disc1'] = float(update.message.text.replace(',', '.'))
-        await send_clean_message(update, context, LOCALIZATION[get_language(context)]['pro_double_enter_second'])
-        return PRO_DOUBLE_DISC2
-    except: return PRO_DOUBLE_DISC1
-
-async def pro_double_disc2_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
-    try:
-        d2 = float(update.message.text.replace(',', '.'))
-        p = context.user_data.get('pro_double_price')
-        d1 = context.user_data.get('pro_double_disc1')
-        final = p * (1-d1/100) * (1-d2/100)
-        res = f"🔁 Двойная\n💰 {p}\n1️⃣ -{d1}%\n2️⃣ -{d2}%\n✅ {final:.2f} грн"
-        await send_clean_message(update, context, res, keep_result=True)
-        add_to_history(context, res)
-        await send_clean_message(update, context, LOCALIZATION[get_language(context)]['next_action_prompt'], reply_markup=get_next_actions_keyboard(context))
-        return ВЫБОР_ТИПА_СКИДКИ
-    except: return PRO_DOUBLE_DISC2
+async def pro_double_price_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
+    price = parse_positive_float(update.message.text)
+    if price is None:
+        await send_clean_message(update, context, LOCALIZATION[get_language(context)]['pro_invalid_number'])
+        return PRO_DOUBLE_PRICE
+    context.user_data['pro_double_price'] = price
+    await send_clean_message(update, context, LOCALIZATION[get_language(context)]['pro_double_enter_first'])
+    return PRO_DOUBLE_DISC1
+
+async def pro_double_disc1_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
+    disc1 = parse_positive_float(update.message.text)
+    if disc1 is None or not (0 < disc1 < 100):
+        await send_clean_message(update, context, LOCALIZATION[get_language(context)]['pro_invalid_number'])
+        return PRO_DOUBLE_DISC1
+    context.user_data['pro_double_disc1'] = disc1
+    await send_clean_message(update, context, LOCALIZATION[get_language(context)]['pro_double_enter_second'])
+    return PRO_DOUBLE_DISC2
+
+async def pro_double_disc2_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
+    d2 = parse_positive_float(update.message.text)
+    p = context.user_data.get('pro_double_price')
+    d1 = context.user_data.get('pro_double_disc1')
+    if d2 is None or not (0 < d2 < 100) or p is None or d1 is None:
+        await send_clean_message(update, context, LOCALIZATION[get_language(context)]['pro_invalid_number'])
+        return PRO_DOUBLE_DISC2
+    final = p * (1-d1/100) * (1-d2/100)
+    res = f"🔁 Двойная\n💰 {p}\n1️⃣ -{d1}%\n2️⃣ -{d2}%\n✅ {final:.2f} грн"
+    await send_clean_message(update, context, res, keep_result=True)
+    add_to_history(context, res)
+    await send_clean_message(update, context, LOCALIZATION[get_language(context)]['next_action_prompt'], reply_markup=get_next_actions_keyboard(context))
+    return ВЫБОР_ТИПА_СКИДКИ
 
 async def pro_compare_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
     if update.callback_query: await update.callback_query.answer()
     context.user_data['попередній_стан'] = PRO_MENU
     await send_clean_message(update, context, LOCALIZATION[get_language(context)]['pro_compare_first_price'])
     return PRO_COMPARE_FIRST_PRICE
 
-async def pro_compare_first_price_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
-    context.user_data['cmp_p1'] = float(update.message.text.replace(',', '.'))
-    await send_clean_message(update, context, LOCALIZATION[get_language(context)]['pro_compare_first_weight'])
-    return PRO_COMPARE_FIRST_WEIGHT
-
-async def pro_compare_first_weight_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
-    context.user_data['cmp_w1'] = float(update.message.text.replace(',', '.'))
-    await send_clean_message(update, context, LOCALIZATION[get_language(context)]['pro_compare_second_price'])
-    return PRO_COMPARE_SECOND_PRICE
-
-async def pro_compare_second_price_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
-    context.user_data['cmp_p2'] = float(update.message.text.replace(',', '.'))
-    await send_clean_message(update, context, LOCALIZATION[get_language(context)]['pro_compare_second_weight'])
-    return PRO_COMPARE_SECOND_WEIGHT
-
-async def pro_compare_second_weight_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
-    w2 = float(update.message.text.replace(',', '.'))
-    p1, w1 = context.user_data['cmp_p1'], context.user_data['cmp_w1']
-    p2 = context.user_data['cmp_p2']
-    kg1 = p1/w1*1000
-    kg2 = p2/w2*1000
-    res = f"⚖️ Сравнение\n1️⃣ {kg1:.2f} грн/кг\n2️⃣ {kg2:.2f} грн/кг\n✅ Выгоднее: {'1' if kg1<kg2 else '2'}"
-    await send_clean_message(update, context, res, keep_result=True)
-    add_to_history(context, res)
-    await send_clean_message(update, context, LOCALIZATION[get_language(context)]['next_action_prompt'], reply_markup=get_next_actions_keyboard(context))
-    return ВЫБОР_ТИПА_СКИДКИ
+async def pro_compare_first_price_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
+    price = parse_positive_float(update.message.text)
+    if price is None:
+        await send_clean_message(update, context, LOCALIZATION[get_language(context)]['pro_invalid_number'])
+        return PRO_COMPARE_FIRST_PRICE
+    context.user_data['cmp_p1'] = price
+    await send_clean_message(update, context, LOCALIZATION[get_language(context)]['pro_compare_first_weight'])
+    return PRO_COMPARE_FIRST_WEIGHT
+
+async def pro_compare_first_weight_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
+    weight = parse_positive_float(update.message.text)
+    if weight is None:
+        await send_clean_message(update, context, LOCALIZATION[get_language(context)]['pro_invalid_number'])
+        return PRO_COMPARE_FIRST_WEIGHT
+    context.user_data['cmp_w1'] = weight
+    await send_clean_message(update, context, LOCALIZATION[get_language(context)]['pro_compare_second_price'])
+    return PRO_COMPARE_SECOND_PRICE
+
+async def pro_compare_second_price_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
+    price = parse_positive_float(update.message.text)
+    if price is None:
+        await send_clean_message(update, context, LOCALIZATION[get_language(context)]['pro_invalid_number'])
+        return PRO_COMPARE_SECOND_PRICE
+    context.user_data['cmp_p2'] = price
+    await send_clean_message(update, context, LOCALIZATION[get_language(context)]['pro_compare_second_weight'])
+    return PRO_COMPARE_SECOND_WEIGHT
+
+async def pro_compare_second_weight_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
+    w2 = parse_positive_float(update.message.text)
+    p1, w1 = context.user_data.get('cmp_p1'), context.user_data.get('cmp_w1')
+    p2 = context.user_data.get('cmp_p2')
+    if w2 is None or p1 is None or w1 is None or p2 is None:
+        await send_clean_message(update, context, LOCALIZATION[get_language(context)]['pro_invalid_number'])
+        return PRO_COMPARE_SECOND_WEIGHT
+    kg1 = p1/w1*1000
+    kg2 = p2/w2*1000
+    res = f"⚖️ Сравнение\n1️⃣ {kg1:.2f} грн/кг\n2️⃣ {kg2:.2f} грн/кг\n✅ Выгоднее: {'1' if kg1<kg2 else '2'}"
+    await send_clean_message(update, context, res, keep_result=True)
+    add_to_history(context, res)
+    await send_clean_message(update, context, LOCALIZATION[get_language(context)]['next_action_prompt'], reply_markup=get_next_actions_keyboard(context))
+    return ВЫБОР_ТИПА_СКИДКИ
 
 async def pro_promo_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
     if update.callback_query: await update.callback_query.answer()
     context.user_data['попередній_стан'] = PRO_MENU
     await send_clean_message(update, context, LOCALIZATION[get_language(context)]['pro_promo_old_price'])
     return PRO_PROMO_OLD
 
-async def pro_promo_old_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
-    context.user_data['promo_old'] = float(update.message.text.replace(',', '.'))
-    await send_clean_message(update, context, LOCALIZATION[get_language(context)]['pro_promo_new_price'])
-    return PRO_PROMO_NEW
-
-async def pro_promo_new_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
-    new_p = float(update.message.text.replace(',', '.'))
-    old_p = context.user_data['promo_old']
-    res = f"📉 Промо\n💵 Было: {old_p}\n💸 Стало: {new_p}\n⬇️ Скидка: {(old_p-new_p)/old_p*100:.1f}%"
-    await send_clean_message(update, context, res, keep_result=True)
-    add_to_history(context, res)
-    await send_clean_message(update, context, LOCALIZATION[get_language(context)]['next_action_prompt'], reply_markup=get_next_actions_keyboard(context))
-    return ВЫБОР_ТИПА_СКИДКИ
+async def pro_promo_old_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
+    old_price = parse_positive_float(update.message.text)
+    if old_price is None:
+        await send_clean_message(update, context, LOCALIZATION[get_language(context)]['pro_invalid_number'])
+        return PRO_PROMO_OLD
+    context.user_data['promo_old'] = old_price
+    await send_clean_message(update, context, LOCALIZATION[get_language(context)]['pro_promo_new_price'])
+    return PRO_PROMO_NEW
+
+async def pro_promo_new_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
+    new_p = parse_positive_float(update.message.text)
+    old_p = context.user_data.get('promo_old')
+    if new_p is None or old_p is None:
+        await send_clean_message(update, context, LOCALIZATION[get_language(context)]['pro_invalid_number'])
+        return PRO_PROMO_NEW
+    res = f"📉 Промо\n💵 Было: {old_p}\n💸 Стало: {new_p}\n⬇️ Скидка: {(old_p-new_p)/old_p*100:.1f}%"
+    await send_clean_message(update, context, res, keep_result=True)
+    add_to_history(context, res)
+    await send_clean_message(update, context, LOCALIZATION[get_language(context)]['next_action_prompt'], reply_markup=get_next_actions_keyboard(context))
+    return ВЫБОР_ТИПА_СКИДКИ
 
 async def pro_margin_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
     if update.callback_query: await update.callback_query.answer()
     context.user_data['попередній_стан'] = PRO_MENU
     await send_clean_message(update, context, LOCALIZATION[get_language(context)]['pro_margin_cost'])
     return PRO_MARGIN_COST
 
-async def pro_margin_cost_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
-    context.user_data['margin_cost'] = float(update.message.text.replace(',', '.'))
-    await send_clean_message(update, context, LOCALIZATION[get_language(context)]['pro_margin_shelf'])
-    return PRO_MARGIN_SHELF
-
-async def pro_margin_shelf_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
-    shelf = float(update.message.text.replace(',', '.'))
-    cost = context.user_data['margin_cost']
-    profit = shelf - cost
-    res = f"📊 Маржа\n💰 Прибыль: {profit:.2f}\n📈 Наценка: {profit/cost*100:.1f}%\n📉 Маржа: {profit/shelf*100:.1f}%"
-    await send_clean_message(update, context, res, keep_result=True)
-    add_to_history(context, res)
-    await send_clean_message(update, context, LOCALIZATION[get_language(context)]['next_action_prompt'], reply_markup=get_next_actions_keyboard(context))
-    return ВЫБОР_ТИПА_СКИДКИ
+async def pro_margin_cost_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
+    cost = parse_positive_float(update.message.text)
+    if cost is None:
+        await send_clean_message(update, context, LOCALIZATION[get_language(context)]['pro_invalid_number'])
+        return PRO_MARGIN_COST
+    context.user_data['margin_cost'] = cost
+    await send_clean_message(update, context, LOCALIZATION[get_language(context)]['pro_margin_shelf'])
+    return PRO_MARGIN_SHELF
+
+async def pro_margin_shelf_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
+    shelf = parse_positive_float(update.message.text)
+    cost = context.user_data.get('margin_cost')
+    if shelf is None or cost is None:
+        await send_clean_message(update, context, LOCALIZATION[get_language(context)]['pro_invalid_number'])
+        return PRO_MARGIN_SHELF
+    profit = shelf - cost
+    res = f"📊 Маржа\n💰 Прибыль: {profit:.2f}\n📈 Наценка: {profit/cost*100:.1f}%\n📉 Маржа: {profit/shelf*100:.1f}%"
+    await send_clean_message(update, context, res, keep_result=True)
+    add_to_history(context, res)
+    await send_clean_message(update, context, LOCALIZATION[get_language(context)]['next_action_prompt'], reply_markup=get_next_actions_keyboard(context))
+    return ВЫБОР_ТИПА_СКИДКИ
 
 async def pro_show_history(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
     if update.callback_query: await update.callback_query.answer()
     hist = context.user_data.get("history", [])
     text = "\n\n".join(hist) if hist else "История пуста"
     await send_clean_message(update, context, text, keep_result=True)
     await send_clean_message(update, context, LOCALIZATION[get_language(context)]['next_action_prompt'], reply_markup=get_next_actions_keyboard(context))
     return ВЫБОР_ТИПА_СКИДКИ
 
 # --- ОБЩИЕ ---
 
-async def back(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
+async def back(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
     lang = get_language(context)
     prev = context.user_data.get('попередній_стан', ВЫБОР_ТИПА_СКИДКИ)
     state_map = {
         ВЫБОР_ТИПА_СКИДКИ: start,
         ОЖИДАНИЕ_СВОЕЙ_СКИДКИ: calculate_shelf_discount,
         ОЖИДАНИЕ_ЦЕНЫ: calculate_shelf_discount,
-        ОЖИДАНИЕ_N: start,
-        ОЖИДАНИЕ_X: calculate_n_plus_x,
-        ОЖИДАНИЕ_ЦЕНЫ_NX: handle_x_input,
-        ОЖИДАНИЕ_ЦЕНЫ_ВЕС: start,
-        ОЖИДАНИЕ_ГРАММОВ: calculate_price_per_kg,
-        ОЖИДАНИЕ_ЦЕНЫ_СО_СКИДКОЙ: calculate_original_price,
-        ОЖИДАНИЕ_ПРОЦЕНТА_СКИДКИ: handle_discounted_price,
+        ОЖИДАНИЕ_N: start,
+        ОЖИДАНИЕ_X: calculate_n_plus_x,
+        ОЖИДАНИЕ_ЦЕНЫ_NX: prompt_x_input,
+        ОЖИДАНИЕ_ЦЕНЫ_ВЕС: start,
+        ОЖИДАНИЕ_ГРАММОВ: calculate_price_per_kg,
+        ОЖИДАНИЕ_ЦЕНЫ_СО_СКИДКОЙ: calculate_original_price,
+        ОЖИДАНИЕ_ПРОЦЕНТА_СКИДКИ: prompt_discount_percent,
         НАСТРОЙКИ: start,
         ВЫБОР_ЯЗЫКА: start,
         PRO_MENU: start,
         PRO_AUTOMODE_INPUT: open_pro_menu,
         PRO_FIXED_PRICE: open_pro_menu,
         PRO_FIXED_DISCOUNT: open_pro_menu,
         PRO_LOYAL_ORIGINAL: open_pro_menu,
         PRO_LOYAL_CARD: open_pro_menu,
         PRO_DOUBLE_PRICE: open_pro_menu,
         PRO_DOUBLE_DISC1: open_pro_menu,
         PRO_DOUBLE_DISC2: open_pro_menu,
         PRO_COMPARE_FIRST_PRICE: open_pro_menu,
         PRO_COMPARE_FIRST_WEIGHT: open_pro_menu,
         PRO_COMPARE_SECOND_PRICE: open_pro_menu,
         PRO_COMPARE_SECOND_WEIGHT: open_pro_menu,
         PRO_PROMO_OLD: open_pro_menu,
         PRO_PROMO_NEW: open_pro_menu,
         PRO_MARGIN_COST: open_pro_menu,
         PRO_MARGIN_SHELF: open_pro_menu,
     }
     handler = state_map.get(prev, start)
     return await handler(update, context)
 
 async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE | None) -> None:
     logger.error(f"Error: {context.error}")
 
 async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
     await send_clean_message(update, context, "Отмена", reply_markup=ReplyKeyboardRemove())
     return ConversationHandler.END
 
-async def restart(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
-    if update.callback_query: await update.callback_query.answer()
-    context.user_data.clear()
-    context.user_data['language'] = 'ru'
-    await start(update, context)
-    return ВЫБОР_ЯЗЫКА
+async def restart(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
+    if update.callback_query: await update.callback_query.answer()
+    context.user_data.clear()
+    context.user_data['language'] = 'ru'
+    return await start(update, context)
 
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
