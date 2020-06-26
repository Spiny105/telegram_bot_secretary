# coding=utf-8
import json
import os
from telethon import TelegramClient, events

# Загрузить настройки из файла
with open("settings.json", "r", encoding="utf-8") as read_file:
    configuration = json.load(read_file)

# Распарсить полученные настройки
allowed_users = configuration.get("allowedUsers")
local_dirs = configuration.get("localDirs")
api_id = configuration.get("api_id")
api_hash = configuration.get("api_hash")
session = configuration.get("session")

# Папка для сохранения данных
dir_number = 0

# Проверить папки для сохранения файлов. Если их нет, то создать
for path in local_dirs:
    try:
        if not os.path.exists(path):
            os.makedirs(path)
    except OSError:
        print("Не могу создать папку!")


# Проверка на то, что пользователь в списке разрешенных
def is_user_allowed(user):
    return user in allowed_users


# Запускаем клинт для взаимодействия с телеграмом
client = TelegramClient(session, api_id, api_hash)


# Реакция на новое сообщение
@client.on(events.NewMessage())
async def normal_handler(event):

    global dir_number
    message = event.message
    sender = await message.get_sender()
    username = sender.username

    # Проверить права доступа
    if not is_user_allowed(username):
        await event.respond('У Вас нет доступа!')
        return

    # Проверить, что в сообщении есть данные
    if message.file:

        # Сохранить данные в заданную папку
        reply = 'Загружаю данные'
        await event.respond(reply)
        await client.download_media(message=message, file=local_dirs[dir_number])
        reply = 'Данные загружены'
        await event.respond(reply)

    # Отправить пользователю список доступных папок
    elif message.message.lower() == "список папок":

        reply = 'Папки для сохранения файлов:\n'
        for i in range(len(local_dirs)):
            reply += str(i) + ': \'' + local_dirs[i] + '\'\n'
        await event.respond(reply)

    # Задать новую папку для сохранения данных
    elif message.message.isdigit():

        try:
            new_dir_number = int(message.message)
            if new_dir_number > len(local_dirs):
                raise ValueError
            dir_number = new_dir_number
            reply = 'Новая папка для сохранения = ' + local_dirs[dir_number]
            await event.respond(reply)

        except ValueError:
            reply = 'Не корректный номер папки'
            await event.respond(reply)
            return
    # Отправить пользователю список команд
    else:

        await event.respond('В сообщении не обнаружены данные\n'
                            '\n'
                            'Доступные команды:\n'
                            'список папок\n'
                            'Для измениния папки введите номер папки\n')

# Запустить клиент
client.start()
client.run_until_disconnected()
