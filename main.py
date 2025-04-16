import telebot
from telebot import types

bot = telebot.TeleBot('8107411693:AAEZd5Fqas_uaRuJiq_1UB75FRSFM6svMDM')

user_data = {}
user_state = {}

COMMUNITY_CHAT_ID = -1002489234995
COMMUNITY_CHAT_LINK = "https://t.me/+cgUkenl_WqdiYWUy"

@bot.message_handler(commands=['help'])
def help_command(message):
    bot.send_message(
        message.chat.id,
        "ℹ️ При возникновении проблем с ботом или чатом — пишите в поддержку: @zarema_7"
    )

@bot.message_handler(commands=['start'])
def start(message):
    chat_id = message.chat.id
    user_data[chat_id] = {}
    user_state[chat_id] = "waiting_name"
    bot.send_message(chat_id, "Привет! Давайте создадим анкету для вашего питомца 🐶. Как зовут собаку?")

@bot.message_handler(func=lambda msg: user_state.get(msg.chat.id) == "waiting_name")
def get_pet_name(message):
    chat_id = message.chat.id
    name = message.text.strip()
    if not name:
        bot.send_message(chat_id, "Пожалуйста, введите имя собаки.")
        return
    user_data[chat_id]['Имя собаки'] = name
    user_state[chat_id] = "waiting_breed"
    bot.send_message(chat_id, "Порода собаки?")

@bot.message_handler(func=lambda msg: user_state.get(msg.chat.id) == "waiting_breed")
def get_breed(message):
    chat_id = message.chat.id
    user_data[chat_id]['Порода'] = message.text
    user_state[chat_id] = "waiting_age"
    bot.send_message(chat_id, "Возраст?")

@bot.message_handler(func=lambda msg: user_state.get(msg.chat.id) == "waiting_age")
def get_age(message):
    chat_id = message.chat.id
    user_data[chat_id]['Возраст'] = message.text
    user_state[chat_id] = "waiting_gender"
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("Самец", "Самка")
    bot.send_message(chat_id, "Пол собаки?", reply_markup=markup)

@bot.message_handler(func=lambda msg: user_state.get(msg.chat.id) == "waiting_gender")
def get_gender(message):
    chat_id = message.chat.id
    user_data[chat_id]['Пол'] = message.text
    user_state[chat_id] = "waiting_owner"
    bot.send_message(chat_id, "Как зовут хозяина?")

@bot.message_handler(func=lambda msg: user_state.get(msg.chat.id) == "waiting_owner")
def get_owner(message):
    chat_id = message.chat.id
    user_data[chat_id]['Хозяин'] = message.text
    user_state[chat_id] = "waiting_city"
    bot.send_message(chat_id, "В каком городе вы находитесь?")

@bot.message_handler(func=lambda msg: user_state.get(msg.chat.id) == "waiting_city")
def get_city(message):
    chat_id = message.chat.id
    user_data[chat_id]['Город'] = message.text
    user_state[chat_id] = "waiting_district"
    bot.send_message(chat_id, "А район?")

@bot.message_handler(func=lambda msg: user_state.get(msg.chat.id) == "waiting_district")
def get_district(message):
    chat_id = message.chat.id
    user_data[chat_id]['Район'] = message.text
    user_state[chat_id] = "waiting_photo"
    bot.send_message(chat_id, "Пришлите фото питомца 🐕")

@bot.message_handler(content_types=['photo'])
def get_photo(message):
    chat_id = message.chat.id
    state = user_state.get(chat_id)

    if state == "waiting_photo":
        user_data[chat_id]['Фото'] = message.photo[-1].file_id
        user_state[chat_id] = "waiting_description"
        bot.send_message(chat_id, "Добавьте краткое описание о питомце:")
    elif state == "editing_photo":
        user_data[chat_id]['Фото'] = message.photo[-1].file_id
        bot.send_message(chat_id, "Фото обновлено ✅")
        show_main_menu(chat_id)
        send_profile(chat_id)
        user_state[chat_id] = None

@bot.message_handler(func=lambda msg: user_state.get(msg.chat.id) == "waiting_photo", content_types=['text', 'document', 'video'])
def wrong_photo_format(message):
    chat_id = message.chat.id
    bot.send_message(chat_id, "❌ Это не фотография. Пожалуйста, отправьте изображение.")

@bot.message_handler(func=lambda msg: user_state.get(msg.chat.id) == "waiting_description", content_types=['text'])
def get_description(message):
    chat_id = message.chat.id
    user_data[chat_id]['Описание'] = message.text
    user_state[chat_id] = None
    show_main_menu(chat_id)
    send_profile(chat_id)
    # сообщение в личный чат
    bot.send_message(chat_id, f"🎉 Теперь вы можете пообщаться с другими владельцами собак в нашем чате:\n{COMMUNITY_CHAT_LINK}")
    # сообщение в группу
    bot.send_message(COMMUNITY_CHAT_ID, "👋 Поприветствуйте нового участника нашего чата!")
    send_profile(COMMUNITY_CHAT_ID, user_id=chat_id)

def show_main_menu(chat_id):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("📄 Показать анкету", "✏️ Редактировать", "🗑 Удалить анкету")
    bot.send_message(chat_id, "Выберите действие:", reply_markup=markup)

def send_profile(chat_id, user_id=None):
    if user_id is None:
        user_id = chat_id
    data = user_data.get(user_id)
    if not data:
        bot.send_message(chat_id, "Анкета не найдена.")
        return
    profile = (
        f"🐶 <b>Имя:</b> {data['Имя собаки']}\n"
        f"📖 <b>Порода:</b> {data['Порода']}\n"
        f"🎂 <b>Возраст:</b> {data['Возраст']}\n"
        f"⚧ <b>Пол:</b> {data['Пол']}\n"
        f"👤 <b>Хозяин:</b> {data['Хозяин']}\n"
        f"📍 <b>Город:</b> {data['Город']}, {data['Район']}\n"
        f"📝 <b>Описание:</b> {data['Описание']}"
    )
    bot.send_photo(chat_id, data['Фото'], caption=profile, parse_mode='HTML')

@bot.message_handler(func=lambda m: m.text == "📄 Показать анкету")
def show_profile_again(message):
    send_profile(message.chat.id)

@bot.message_handler(func=lambda m: m.text == "🗑 Удалить анкету")
def delete_profile(message):
    chat_id = message.chat.id
    user_data.pop(chat_id, None)
    bot.send_message(chat_id, "Анкета удалена 🗑")
    show_main_menu(chat_id)

@bot.message_handler(func=lambda m: m.text == "✏️ Редактировать")
def edit_profile(message):
    chat_id = message.chat.id
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    fields = {
        "🐶 Имя собаки", "📖 Порода", "🎂 Возраст", "⚧ Пол",
        "👤 Хозяин", "📍 Город", "📍 Район", "📝 Описание", "🖼 Фото"
    }
    for field in fields:
        markup.add(field)
    bot.send_message(chat_id, "Что вы хотите изменить?", reply_markup=markup)

@bot.message_handler(func=lambda m: m.text in {
    "🐶 Имя собаки", "📖 Порода", "🎂 Возраст", "⚧ Пол",
    "👤 Хозяин", "📍 Город", "📍 Район", "📝 Описание", "🖼 Фото"
})
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
    if field == "Фото":
        user_state[chat_id] = "editing_photo"
        bot.send_message(chat_id, "Пришлите новое фото питомца 🖼")
    else:
        user_state[chat_id] = f"editing_{field}"
        bot.send_message(chat_id, f"Введите новое значение для «{field}»:")

@bot.message_handler(func=lambda m: user_state.get(m.chat.id, "").startswith("editing_"))
def apply_edit(message):
    chat_id = message.chat.id
    field = user_state[chat_id].replace("editing_", "")
    user_data[chat_id][field] = message.text
    user_state[chat_id] = None
    bot.send_message(chat_id, f"{field} обновлено ✅")
    show_main_menu(chat_id)
    send_profile(chat_id)

bot.polling(none_stop=True)


