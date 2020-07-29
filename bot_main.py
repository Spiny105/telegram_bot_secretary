# coding=utf-8
import json
from telethon import TelegramClient, events
from bot_actions import *

# Для работы с консолью
win_console_mode = False
bot_working_dir = os.getcwd()

# Загрузить настройки из файла
with open("settings.json", "r", encoding="utf-8") as read_file:
    configuration = json.load(read_file)

# Распарсить полученные настройки
allowed_users = configuration.get("allowedUsers")
local_dirs = configuration.get("localDirs")
api_id = configuration.get("api_id")
api_hash = configuration.get("api_hash")
session = configuration.get("session")

# Создать профили пользователей
profiles = dict().fromkeys(allowed_users, local_dirs[0])

# Проверить папки для сохранения файлов. Если их нет, то создать
check_folders(folders=local_dirs)

# Запускаем клинт для взаимодействия с телеграмом
client = TelegramClient(session, api_id, api_hash)

# Включить загрузку файлов
download_enabled = True

start_required = True

# Реакция на новое сообщение
@client.on(events.NewMessage())
async def normal_handler(event):

    global profiles
    global download_enabled
    global start_required
    global win_console_mode

    message = event.message
    sender = await message.get_sender()
    username = sender.username

    # Проверить права доступа
    if username not in allowed_users:
        await event.respond('У Вас нет доступа!')
        return

    # Включить/выключить режим консоли
    if event.message.message.lower() == 'cmdon':
        await event.respond('Включен режим консоли Windows \n' + cmd_exec_command('echo %cd%'))
        win_console_mode = True
        return

    if event.message.message.lower() == 'cmdoff':
        os.chdir(bot_working_dir)
        await event.respond('Выключен режим консоли Windows')
        win_console_mode = False
        return

    # Взаимодействие с консолью
    if win_console_mode:
        await cmd_interact(event=event)
        return

    # Загрузить прикрепленные файлы, если они есть в сообщении
    attachment_found = await get_attached_files_from_message(client=client, event=event,
                                                             folder=profiles.get(username),
                                                             download_enabled=download_enabled)

    # Проверить на наличие ссылок на Яндекс.Диск
    links_found = await get_cloud_services_files_from_message(event=event, folder=profiles.get(username),
                                                              download_enabled=download_enabled)

    # Выход
    if event.message.message.lower() == 'exit':
        exit(1)

    # Если в сообщении были найдены данные, то выход
    if links_found or attachment_found:
        return

    # Отправить пользователю список доступных папок
    if await process_showf_command(event=event, folders=local_dirs):
        return

    # Отправить пользователю список команд
    if await process_help_command(event=event):
        return

    # Команда stop
    if await process_stop_command(event=event):
        download_enabled = False
        return

    # Команда start
    if await process_start_command(event=event):
        download_enabled = True
        return

    # Перезапуск бота
    if message.message.lower() == "restart":
        start_required = True
        await event.respond('Перезапуск бота')
        await client.disconnect()
        return

    # Задать текущую папку для сохранения данных
    if await process_specify_folder_command(event=event, folders=local_dirs,
                                            sender=sender, users=profiles):
        return


# Запустить клиент
while start_required:
    start_required = False
    print("Запуск клиента")
    client.start()
    client.run_until_disconnected()
