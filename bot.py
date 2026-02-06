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


async def handle_nx_price_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:␊
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

async def prompt_x_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    lang = get_language(context)
    if update.callback_query:
        await update.callback_query.answer()
    if context.user_data.get('n') is None:
        return await calculate_n_plus_x(update, context)
    context.user_data['попередній_стан'] = ОЖИДАНИЕ_N
    await send_clean_message(
        update,
        context,
        LOCALIZATION[lang]['enter_x'],
        reply_markup=get_numeric_reply_keyboard(),
    )
    return ОЖИДАНИЕ_X

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
@@ -859,58 +874,61 @@ async def pro_handle_automode(update: Update, context: ContextTypes.DEFAULT_TYPE
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

async def pro_fixed_price_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    try:
        price = float(update.message.text.replace(',', '.'))
        if price <= 0:
            raise ValueError("price must be positive")
        context.user_data['pro_fixed_price'] = price
        await send_clean_message(update, context, LOCALIZATION[get_language(context)]['pro_fixed_enter_discount_sum'])
        return PRO_FIXED_DISCOUNT
    except:
        await send_clean_message(update, context, LOCALIZATION[get_language(context)]['pro_invalid_number'])
        return PRO_FIXED_PRICE

async def pro_fixed_discount_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    try:
        disc = float(update.message.text.replace(',', '.'))
        price = context.user_data.get('pro_fixed_price')
        await delete_mode_message(update, context)
        res = f"💸 Фикс. скидка\n💰 Цена: {price}\n⬇️ Скидка: {disc}\n✅ Итог: {price-disc:.2f} грн"
        await send_clean_message(update, context, res, keep_result=True)
        add_to_history(context, res)
        await send_clean_message(update, context, LOCALIZATION[get_language(context)]['next_action_prompt'], reply_markup=get_next_actions_keyboard(context))
        return ВЫБОР_ТИПА_СКИДКИ
    except: return PRO_FIXED_DISCOUNT

async def pro_loyal_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if update.callback_query: await update.callback_query.answer()
    context.user_data['попередній_стан'] = PRO_MENU
    await send_clean_message(update, context, LOCALIZATION[get_language(context)]['pro_loyal_enter_regular'])
    return PRO_LOYAL_ORIGINAL

async def pro_loyal_original_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    try:
        context.user_data['pro_loyal_original'] = float(update.message.text.replace(',', '.'))
        await send_clean_message(update, context, LOCALIZATION[get_language(context)]['pro_loyal_enter_card'])
        return PRO_LOYAL_CARD
    except: return PRO_LOYAL_ORIGINAL
@@ -1028,53 +1046,53 @@ async def pro_margin_shelf_input(update: Update, context: ContextTypes.DEFAULT_T
    cost = context.user_data['margin_cost']
    profit = shelf - cost
    res = f"📊 Маржа\n💰 Прибыль: {profit:.2f}\n📈 Наценка: {profit/cost*100:.1f}%\n📉 Маржа: {profit/shelf*100:.1f}%"
    await send_clean_message(update, context, res, keep_result=True)
    add_to_history(context, res)
    await send_clean_message(update, context, LOCALIZATION[get_language(context)]['next_action_prompt'], reply_markup=get_next_actions_keyboard(context))
    return ВЫБОР_ТИПА_СКИДКИ

async def pro_show_history(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if update.callback_query: await update.callback_query.answer()
    hist = context.user_data.get("history", [])
    text = "\n\n".join(hist) if hist else "История пуста"
    await send_clean_message(update, context, text, keep_result=True)
    await send_clean_message(update, context, LOCALIZATION[get_language(context)]['next_action_prompt'], reply_markup=get_next_actions_keyboard(context))
    return ВЫБОР_ТИПА_СКИДКИ

# --- ОБЩИЕ ---

async def back(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    lang = get_language(context)
    prev = context.user_data.get('попередній_стан', ВЫБОР_ТИПА_СКИДКИ)
    state_map = {
        ВЫБОР_ТИПА_СКИДКИ: start,
        ОЖИДАНИЕ_СВОЕЙ_СКИДКИ: calculate_shelf_discount,
        ОЖИДАНИЕ_ЦЕНЫ: calculate_shelf_discount,
        ОЖИДАНИЕ_N: start,␊
        ОЖИДАНИЕ_X: calculate_n_plus_x,␊
        ОЖИДАНИЕ_ЦЕНЫ_NX: prompt_x_input,
        ОЖИДАНИЕ_ЦЕНЫ_ВЕС: start,
        ОЖИДАНИЕ_ГРАММОВ: calculate_price_per_kg,
        ОЖИДАНИЕ_ЦЕНЫ_СО_СКИДКОЙ: calculate_original_price,
        ОЖИДАНИЕ_ПРОЦЕНТА_СКИДКИ: handle_discounted_price,
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
