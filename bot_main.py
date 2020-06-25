# coding=utf-8
import json
import os
from telethon import TelegramClient, events

# ключить/выключить отладку
debug_mode = 0

# Загрузить настройки из файла
with open("settings.json", "r", encoding="utf-8") as read_file:
    configuration = json.load(read_file)

# Распарсить полученные настройки
allowed_users = configuration.get("allowedUsers")
local_dirs = configuration.get("localDirs")
api_id = configuration.get("api_id")
api_hash = configuration.get("api_hash")
session = configuration.get("session")
last_received_message = None


# Отправить сообщение о том, что идет сохранение предидущих данных
async def send_prev_incomplete_receive_detected(event):
    reply = 'Сначала должно быть завершено сохранение прошлых данных!\n' \
            'Пользователь  = ' + last_received_message.sender.username
    await event.respond(reply)


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

    global debug_mode
    global last_received_message
    global selected_dir_for_saving

    message = event.message
    sender = await message.get_sender()
    username = sender.username

    if debug_mode:
        dest = 'morin_2_bot'
    else:
        dest = username

    # Проверить права доступа
    if not is_user_allowed(username):
        await event.respond('У Вас нет доступа!')
        return

    # Проверить - это сообщение с данными, или с выбором папки
    if not message.file:
        # Проверить, что команду отправил тот же самый пользователь
        last_user = last_received_message.chat.username
        if not (username == last_user):
            await send_prev_incomplete_receive_detected(event)
            return

        # Получить из ответа номер папки для скачивания
        try:
            dir_number = int(message.message)
        except ValueError:
            reply = 'Не удалось получить номер папки. Попробуйте снова'
            await event.respond(reply)
            return

        # Сохранить полученные данные
        reply = 'Загружаю данные'
        await event.respond(reply)

        await client.download_media(message=last_received_message, file=local_dirs[dir_number])

        reply = 'Данные загружены'
        await event.respond(reply)

        last_received_message = None
        return
    elif not last_received_message is None:
        await send_prev_incomplete_receive_detected(event)
        return

    # Отправить ответ с вариантами того, куда сохранить полученные файлы
    reply = 'Папки для сохранения файлов:\n'
    for i in range(len(local_dirs)):
        reply += str(i) + ': \'' + local_dirs[i] + '\'\n'
    reply += '\n Введите цифру с номером папки'
    last_received_message = message
    await event.respond(reply)

# Запустить клиент
client.start()
client.run_until_disconnected()
