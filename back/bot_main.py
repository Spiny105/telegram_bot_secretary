# coding=utf-8
import json
from telethon import TelegramClient, events
from telethon.events.newmessage import NewMessage
from bot_actions import *
import threading
import time


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
yandex_disk_dir = configuration.get("yandex_disk_dir")

# Период опроса папки Я.Диск
YANDEX_DISK_FOLDER_SIZE_CHECH_PERIOD = 3.0

# Создать профили пользователей
profiles = dict().fromkeys(allowed_users, local_dirs[0])

# Проверить папки для сохранения файлов. Если их нет, то создать
check_folders(folders=local_dirs)

# Включить загрузку файлов
download_enabled = True

# start_required = True

# Клиент для взаимодействия с телеграмом
client = TelegramClient(session, api_id, api_hash)


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
    # if await process_stop_command(event=event):
    #     download_enabled = False
    #     return

    # Команда start
    # if await process_start_command(event=event):
    #     download_enabled = True
    #     return

    # Перезапуск бота
    # if message.message.lower() == "restart":
    #     start_required = True
    #     await event.respond('Перезапуск бота')
    #     await client.disconnect()
    #     return

    # Задать текущую папку для сохранения данных
    if await process_specify_folder_command(event=event, folders=local_dirs,
                                            sender=sender, users=profiles):
        return


# Получить размер папки
def get_folder_size(start_path='.'):
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(start_path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            total_size += os.path.getsize(fp)
    print(total_size)
    return total_size


# Циклическая проверка папки Я.Диск
curr_ya_disk_folder_size = get_folder_size(yandex_disk_dir)
prev_ya_disk_folder_size = curr_ya_disk_folder_size


# def start_yandex_folder_size_service():
#     global curr_ya_disk_folder_size
#     global prev_ya_disk_folder_size
#     global client
#
#     # # Получить размер папки Яндекс.Диск
#     # time.sleep(YANDEX_DISK_FOLDER_SIZE_CHECH_PERIOD)
#     # curr_ya_disk_folder_size = get_folder_size(yandex_disk_dir)
#     # if curr_ya_disk_folder_size > prev_ya_disk_folder_size:
#     #     while True:
#     #         prev_ya_disk_folder_size = curr_ya_disk_folder_size
#     #         time.sleep(YANDEX_DISK_FOLDER_SIZE_CHECH_PERIOD)
#     #         curr_ya_disk_folder_size = get_folder_size(yandex_disk_dir)
#     #         if curr_ya_disk_folder_size == get_folder_size(yandex_disk_dir):
#     #             for user in allowed_users:
#     #                 await client.send_message(user, "Что-то загрузилось на Я.Диск")
#     #             break
#
#
#
#     my_timer = threading.2Timer(YANDEX_DISK_FOLDER_SIZE_CHECH_PERIOD, start_yandex_folder_size_service)
#     my_timer.start()


# Запускаем клиент для взаимодействия с телеграмом
with client:
    client.start()
    client.run_until_disconnected()


# async def main():
#     while True:
#         pass
    # prev_ya_disk_folder_size = get_folder_size(yandex_disk_dir)
    #
    # while True:
    #     # Получить размер папки Яндекс.Диск
    #     time.sleep(15)
    #     curr_ya_disk_folder_size = get_folder_size(yandex_disk_dir)
    #     if curr_ya_disk_folder_size > prev_ya_disk_folder_size:
    #         while True:
    #             prev_ya_disk_folder_size = curr_ya_disk_folder_size
    #             time.sleep(15)
    #             curr_ya_disk_folder_size = get_folder_size(yandex_disk_dir)
    #             if curr_ya_disk_folder_size == get_folder_size(yandex_disk_dir):
    #                 for user in allowed_users:
    #                     await client.send_message(user, "Что-то загрузилось на Я.Диск")
    #                 break


# with client:
#     client.start()
#     client.run_until_disconnected()


