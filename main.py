import telebot
from telebot import types

bot = telebot.TeleBot('8107411693:AAF-dQy6VBa7AHYMmR05X2MWgiPgP56osk4')

user_data = {}  # chat_id -> list of profiles
user_state = {}  # chat_id -> state
active_index = {}  # chat_id -> current profile index

COMMUNITY_CHAT_ID = -1002489234995
COMMUNITY_CHAT_LINK = "https://t.me/+cgUkenl_WqdiYWUy"

@bot.message_handler(commands=['help'])
def help_command(message):
    bot.send_message(message.chat.id, "ℹ️ При возникновении проблем с ботом или чатом — пишите в поддержку: @zarema_7")

@bot.message_handler(commands=['start'])
def start(message):
    chat_id = message.chat.id
    user_data.setdefault(chat_id, [])
    user_data[chat_id].append({})
    active_index[chat_id] = len(user_data[chat_id]) - 1
    user_state[chat_id] = "waiting_name"
    bot.send_message(chat_id, "Привет! Давайте создадим анкету для вашего питомца 🐶. Как зовут собаку?")

@bot.message_handler(func=lambda msg: user_state.get(msg.chat.id) == "waiting_name")
def get_pet_name(message):
    chat_id = message.chat.id
    name = message.text.strip()
    if not name:
        bot.send_message(chat_id, "Пожалуйста, введите имя собаки.")
        return
    user_data[chat_id][active_index[chat_id]]['Имя собаки'] = name
    user_state[chat_id] = "waiting_breed"
    bot.send_message(chat_id, "Порода собаки?")

@bot.message_handler(func=lambda msg: user_state.get(msg.chat.id) == "waiting_breed")
def get_breed(message):
    chat_id = message.chat.id
    user_data[chat_id][active_index[chat_id]]['Порода'] = message.text
    user_state[chat_id] = "waiting_age"
    bot.send_message(chat_id, "Возраст?")

@bot.message_handler(func=lambda msg: user_state.get(msg.chat.id) == "waiting_age")
def get_age(message):
    chat_id = message.chat.id
    user_data[chat_id][active_index[chat_id]]['Возраст'] = message.text
    user_state[chat_id] = "waiting_gender"
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("Самец", "Самка")
    bot.send_message(chat_id, "Пол собаки?", reply_markup=markup)

@bot.message_handler(func=lambda msg: user_state.get(msg.chat.id) == "waiting_gender")
def get_gender(message):
    chat_id = message.chat.id
    user_data[chat_id][active_index[chat_id]]['Пол'] = message.text
    user_state[chat_id] = "waiting_owner"
    bot.send_message(chat_id, "Как зовут хозяина?")

@bot.message_handler(func=lambda msg: user_state.get(msg.chat.id) == "waiting_owner")
def get_owner(message):
    chat_id = message.chat.id
    user_data[chat_id][active_index[chat_id]]['Хозяин'] = message.text
    user_state[chat_id] = "waiting_city"
    bot.send_message(chat_id, "В каком городе вы находитесь?")

@bot.message_handler(func=lambda msg: user_state.get(msg.chat.id) == "waiting_city")
def get_city(message):
    chat_id = message.chat.id
    user_data[chat_id][active_index[chat_id]]['Город'] = message.text
    user_state[chat_id] = "waiting_district"
    bot.send_message(chat_id, "А район?")

@bot.message_handler(func=lambda msg: user_state.get(msg.chat.id) == "waiting_district")
def get_district(message):
    chat_id = message.chat.id
    user_data[chat_id][active_index[chat_id]]['Район'] = message.text
    user_state[chat_id] = "waiting_photo"
    bot.send_message(chat_id, "Пришлите фото питомца 🐕")

@bot.message_handler(content_types=['photo'])
def get_photo(message):
    chat_id = message.chat.id
    state = user_state.get(chat_id)
    if state == "waiting_photo":
        user_data[chat_id][active_index[chat_id]]['Фото'] = message.photo[-1].file_id
        user_state[chat_id] = "waiting_description"
        bot.send_message(chat_id, "Добавьте краткое описание о питомце:")
    elif state == "editing_photo":
        user_data[chat_id][active_index[chat_id]]['Фото'] = message.photo[-1].file_id
        bot.send_message(chat_id, "Фото обновлено ✅")
        show_main_menu(chat_id)
        send_profile(chat_id)
        user_state[chat_id] = None

@bot.message_handler(func=lambda msg: user_state.get(msg.chat.id) == "waiting_description", content_types=['text'])
def get_description(message):
    chat_id = message.chat.id
    user_data[chat_id][active_index[chat_id]]['Описание'] = message.text
    user_state[chat_id] = None
    send_profile(chat_id)
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("✅ Добавляем анкету")
    bot.send_message(chat_id, "📌 Анкета готова! Она будет опубликована в чате после подтверждения.", reply_markup=markup)

@bot.message_handler(func=lambda m: m.text == "✅ Добавляем анкету")
def confirm_publish(message):
    uid = message.chat.id
    if uid not in active_index:
        bot.send_message(uid, "Ошибка: не выбрана анкета для публикации.")
        return
    i = active_index[uid]
    send_profile(COMMUNITY_CHAT_ID, uid, i)
    bot.send_message(COMMUNITY_CHAT_ID, "👋 Поприветствуйте нового участника!")
    bot.send_message(uid, "Анкета добавлена ✅")
    show_main_menu(uid)

@bot.message_handler(func=lambda m: m.text.startswith("📄 Показать"))
def show_profile_numbered(message):
    chat_id = message.chat.id
    try:
        index = int(message.text.split()[-1]) - 1
        if index >= len(user_data.get(chat_id, [])):
            bot.send_message(chat_id, "Такой анкеты не существует.")
            return
        active_index[chat_id] = index
        send_profile(chat_id)
    except:
        bot.send_message(chat_id, "Невозможно отобразить анкету.")

@bot.message_handler(func=lambda m: m.text == "🗑 Удалить анкету")
def ask_delete_which(message):
    chat_id = message.chat.id
    profiles = user_data.get(chat_id, [])
    if not profiles:
        bot.send_message(chat_id, "У вас нет анкет для удаления.")
        return
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for i in range(len(profiles)):
        markup.add(f"Удалить анкету {i+1}")
    bot.send_message(chat_id, "Выберите анкету для удаления:", reply_markup=markup)

@bot.message_handler(func=lambda m: m.text.startswith("Удалить анкету"))
def delete_selected_profile(message):
    chat_id = message.chat.id
    try:
        index = int(message.text.split()[-1]) - 1
        profiles = user_data.get(chat_id, [])
        if index >= len(profiles):
            bot.send_message(chat_id, "Анкета не найдена.")
            return
        user_data[chat_id].pop(index)
        bot.send_message(chat_id, f"Анкета {index+1} удалена 🗑")
        if not user_data[chat_id]:
            user_data[chat_id].append({})
        active_index[chat_id] = max(0, len(user_data[chat_id]) - 1)
        show_main_menu(chat_id)
    except:
        bot.send_message(chat_id, "Ошибка при удалении анкеты.")

@bot.message_handler(func=lambda m: m.text == "➕ Добавить новую анкету")
def add_new_profile(message):
    chat_id = message.chat.id
    user_data[chat_id].append({})
    active_index[chat_id] = len(user_data[chat_id]) - 1
    user_state[chat_id] = "waiting_name"
    bot.send_message(chat_id, "Добавляем новую анкету 🐶. Как зовут собаку?")

@bot.message_handler(func=lambda m: m.text == "✏️ Редактировать")
def edit_profile(message):
    chat_id = message.chat.id
    profiles = user_data.get(chat_id, [])
    if not profiles:
        bot.send_message(chat_id, "Нет анкет для редактирования.")
        return
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for i in range(len(profiles)):
        markup.add(f"Редактировать анкету {i+1}")
    bot.send_message(chat_id, "Выберите анкету для редактирования:", reply_markup=markup)

@bot.message_handler(func=lambda m: m.text.startswith("Редактировать анкету"))
def choose_edit_index(message):
    chat_id = message.chat.id
    try:
        index = int(message.text.split()[-1]) - 1
        if index >= len(user_data.get(chat_id, [])):
            bot.send_message(chat_id, "Анкета не найдена.")
            return
        active_index[chat_id] = index
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        fields = ["🐶 Имя собаки", "📖 Порода", "🎂 Возраст", "⚧ Пол", "👤 Хозяин", "📍 Город", "📍 Район", "📝 Описание", "🖼 Фото"]
        for field in fields:
            markup.add(field)
        bot.send_message(chat_id, "Что вы хотите изменить?", reply_markup=markup)
    except:
        bot.send_message(chat_id, "Ошибка выбора анкеты.")

@bot.message_handler(func=lambda m: m.text in ["🐶 Имя собаки", "📖 Порода", "🎂 Возраст", "⚧ Пол", "👤 Хозяин", "📍 Город", "📍 Район", "📝 Описание", "🖼 Фото"])
def handle_edit_choice(message):
    chat_id = message.chat.id
    mapping = {
        "🐶 Имя собаки": "Имя собаки",
        "📖 Порода": "Порода",
        "🎂 Возраст": "Возраст",
        "⚧ Пол": "Пол",
        "👤 Хозяин": "Хозяин",
        "📍 Город": "Город",
        "📍 Район": "Район",
        "📝 Описание": "Описание",
        "🖼 Фото": "Фото"
    }
    field = mapping[message.text]
    index = active_index.get(chat_id, 0)
    if index >= len(user_data.get(chat_id, [])):
        bot.send_message(chat_id, "Анкета не найдена или удалена.")
        return
    if field == "Фото":
        user_state[chat_id] = "editing_photo"
        bot.send_message(chat_id, "Пришлите новое фото питомца 🖼")
    else:
        user_state[chat_id] = f"editing_{field}"
        bot.send_message(chat_id, f"Введите новое значение для «{field}»:")

@bot.message_handler(func=lambda m: isinstance(user_state.get(m.chat.id), str) and user_state[m.chat.id].startswith("editing_"))
def apply_edit(message):
    chat_id = message.chat.id
    field = user_state[chat_id].replace("editing_", "")
    user_data[chat_id][active_index[chat_id]][field] = message.text
    user_state[chat_id] = None
    bot.send_message(chat_id, f"{field} обновлено ✅")
    show_main_menu(chat_id)
    send_profile(chat_id)

def show_main_menu(chat_id):
    profiles = user_data.get(chat_id, [])
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)

    if profiles and any(profiles):  # добавляем кнопки показа анкет только если есть непустые
        for i in range(len(profiles)):
            markup.add(f"📄 Показать анкету {i+1}")

    markup.add("➕ Добавить новую анкету")
    markup.add("✏️ Редактировать", "🗑 Удалить анкету")
    bot.send_message(chat_id, "Выберите действие:", reply_markup=markup)


def send_profile(chat_id, user_id=None, index=None):
    user_id = user_id if user_id is not None else chat_id
    index = index if index is not None else active_index.get(user_id, 0)
    data_list = user_data.get(user_id, [])
    if index >= len(data_list):
        bot.send_message(chat_id, "Анкета не найдена.")
        return
    data = data_list[index]
    profile = (
        f"🐶 <b>Имя:</b> {data.get('Имя собаки', '')}\n"
        f"📖 <b>Порода:</b> {data.get('Порода', '')}\n"
        f"🎂 <b>Возраст:</b> {data.get('Возраст', '')}\n"
        f"⚧ <b>Пол:</b> {data.get('Пол', '')}\n"
        f"👤 <b>Хозяин:</b> {data.get('Хозяин', '')}\n"
        f"📍 <b>Город:</b> {data.get('Город', '')}, {data.get('Район', '')}\n"
        f"📝 <b>Описание:</b> {data.get('Описание', '')}"
    )
    bot.send_photo(chat_id, data.get('Фото'), caption=profile, parse_mode='HTML')

bot.polling(none_stop=True)
