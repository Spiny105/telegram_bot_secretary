# coding=utf-8
import telebot
from telebot import types
import json
import os

# Загрузить настройки из файла
with open("settings.json", "r", encoding="utf-8") as read_file:
    configuration = json.load(read_file)

# Распарсиить полученные настройки
token = configuration.get('telegramToken')
allowed_users = configuration.get("allowedUsers")
local_dirs = configuration.get("localDirs")

# Проверить папки для сохранения файлов. Если их нет, то создать
for path in local_dirs:
    try:
        if not os.path.exists(path):
            os.makedirs(path)
    except OSError:
        print("Не могу создать папку!")

# Запустить бота
bot = telebot.TeleBot(token)

# Здесь хранятся данные о последнем принятом сообщении с файлом
messages_with_file = None


# Проверка на то, что пользователь в списке разрешенных
def is_user_allowed(message):
    user = message.chat.username
    return user in allowed_users


# Нарисовать кнопки по списку папок для сохрания
def draw_save_buttons(dirs):
    keyboard = types.InlineKeyboardMarkup()
    for item in dirs:
        key = types.InlineKeyboardButton(text=item, callback_data=item)
        keyboard.add(key)
    return keyboard


# Реакция на сообщение (без файла)
@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    if is_user_allowed(message):
        bot.send_message(message.from_user.id, "Привет! Рад, что ты мне пишешь!")
    else:
        bot.send_message(message.from_user.id, "У Вас нет доступа")


# Реакция на сообщение с прикрепленным файлом
@bot.message_handler(content_types=['document'])
def handle_file(message):

    # Проверить отправителя
    if not is_user_allowed(message):
        bot.send_message(message.from_user.id, "У Вас нет прав доступа.")
        return

    # Нарисовать кнопочки для сохранения в определенную папку
    buttons = draw_save_buttons(local_dirs)

    # Сохранить последнее сообщение с сохраненными файлами
    global messages_with_file
    messages_with_file = message

    # Отправить кнопки пользователю
    bot.send_message(message.from_user.id, text="Куда сохранить файл?", reply_markup=buttons)


@bot.callback_query_handler(func=lambda call: True)
def callback_worker(call):

    # Определяем нажатую кнопку (и, соответственно, папку для сохранения файла)
    selected_path = call.data

    # Проверяем нет ли уже такого файла. Если есть, то дописать цифру к имени файла
    file_name = messages_with_file.document.file_name
    counter = 1
    initial_file_name = file_name
    while os.path.exists(selected_path + file_name):
        file_name = initial_file_name + "_" + str(counter)
        counter = counter + 1

    # Сохраняем файл в указанную папку
    try:
        chat_id = messages_with_file.chat.id
        file_info = bot.get_file(messages_with_file.document.file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        src = selected_path + file_name
        with open(src, 'wb') as new_file:
            new_file.write(downloaded_file)
        bot.reply_to(messages_with_file, "Файл сохранен с именем = " + file_name)
    except Exception as e:
        bot.reply_to(messages_with_file, e)


# Handle all other messages.
@bot.message_handler(func=lambda message: True, content_types=['audio', 'photo', 'voice', 'video', 'document', 'text', 'location', 'contact', 'sticker'])
def default_command(message):
    bot.send_message(message.chat.id, "This is the default command handler.")

        
# Задать непрерывный опрос телеграма на наличие новых сообщений
bot.polling(none_stop=True, interval=0)
