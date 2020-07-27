# coding=utf-8
import os
import re
import shutil
import zipfile
import urllib.parse
import subprocess

# help - вывод списка всех команд                           +

# showf - показать список папок                             +
# showd - показать список загрузок (% или байты)            ---
# addf - добавить постоянную папку назначения в программу   ---
# delf - удалить постоянную папку из программы              ---

# restart - перезапуск со сбросом/остановкой всех загрузок  +-
# stop - приостановить бота                                 +-
# start - запустить бота                                    +-
from pip._vendor.distlib.compat import raw_input


def check_folders(folders):
    for path in folders:
        try:
            if not os.path.exists(path):
                os.makedirs(path)
        except OSError:
            print("Не могу создать папку!")


# Распаковка файла с переименовыванием крякозыбр
def unpack_zipfile(file, extract_dir, encoding='cp437'):
    with zipfile.ZipFile(file) as archive:
        for entry in archive.infolist():
            # name = entry.filename.encode('cp437').decode(encoding)
            name = entry.filename

            if name.startswith('/') or '..' in name:
                continue

            target = os.path.join(extract_dir, *name.split('/'))
            os.makedirs(os.path.dirname(target), exist_ok=True)
            if not entry.is_dir():  # file
                with archive.open(entry) as source, open(target, 'wb') as dest:
                    shutil.copyfileobj(source, dest)


# Загрузка файл с Яндекс.Диск по ссылке
def get_file_from_yandex_disk(public_key, dir_for_save):

    import requests
    from urllib.parse import urlencode

    base_url = 'https://cloud-api.yandex.net/v1/disk/public/resources/download?'

    # Получаем загрузочную ссылку
    final_url = base_url + urlencode(dict(public_key=public_key))
    response = requests.get(final_url)
    download_url = response.json()['href']

    # Загружаем файл
    download_response = requests.get(download_url)

    # Получаем имя файлам + перевести в читаемый вид (если есть НЕ латинские символы)
    filename = urllib.parse.unquote(download_response.headers.get('Content-Disposition'))[29:]

    # Загружаем файл
    full_file_path = dir_for_save + filename
    with open(full_file_path, 'wb') as f:  # Здесь укажите нужный путь к файлу
        f.write(download_response.content)

    # Распаковываем если это архив, то распаковать, а потом удалить
    if zipfile.is_zipfile(full_file_path):
        unpack_zipfile(full_file_path, dir_for_save, encoding='cp866')
        os.remove(full_file_path)


# Загрузить из сообщения файлы из облака по ссылке
async def get_cloud_services_files_from_message(event, folder, download_enabled):
    message = event.message
    if r"https://yadi.sk" in message.message:

        if not download_enabled:
            await event.respond('Загрузка новых файлов приостановлена. Не загружено')
            return False

        regex = "https:\/\/yadi.sk\S*"
        links = re.findall(regex, message.message)

        for item in links:
            reply = 'Загружаю данные'
            await event.respond(reply)
            get_file_from_yandex_disk(public_key=item, dir_for_save=folder)
            reply = 'Данные загружены'
            await event.respond(reply)
        return True
    else:
        return False


# Загрузить из сообщения прикрепленные файлы
async def get_attached_files_from_message(client, event, folder, download_enabled):
    message = event.message
    if message.file:

        if not download_enabled:
            await event.respond('Загрузка новых файлов приостановлена. Не загружено')
            return False

        # Сохранить данные в заданную папку
        reply = 'Загружаю данные'
        await event.respond(reply)

        result = await client.download_media(message=message, file=folder)
        if result:
            reply = 'Данные загружены'
        else:
            reply = 'Ошибка загрузки данных!'
        await event.respond(reply)
        return True
    else:
        return False


# Обработчик команды help
async def process_help_command(event):
    processed = False
    if event.message.message.lower() == "help":
        await event.respond('help - вывод списка всех команд \n'
                            'showf - показать список папок \n'
                            '%number% - задать номер папки \n'
                            'stop - приостановить бота, старые загрузки продолжаются \n'
                            'start - запустить бота \n'
                            'restart - перезапуск со сбросом/остановкой всех загрузок \n'
                            'cmdon - включить режим консоли Windows'
                            'cmdoff - выключить режим консоли Windows'
                            'cmd %command% - консоль Windows\n')
        processed = True
    return processed


# Обработчик команды showf
async def process_showf_command(event, folders):
    processed = False
    if event.message.message.lower() == "showf":

        reply = 'Папки для сохранения файлов:\n'
        for i in range(len(folders)):
            reply += str(i) + ': \'' + folders[i] + '\'\n'
        await event.respond(reply)
        processed = True
    return processed


# Обработчик команды определения папки для сохранения данных
async def process_specify_folder_command(event, folders, sender, users):
    success = True
    message = event.message
    username = sender.username
    if message.message.isdigit():

        try:
            new_dir_number = int(message.message)
            if new_dir_number > len(folders):
                raise ValueError
            users.update({username: folders[new_dir_number]})
            reply = 'Новая папка для сохранения = ' + users.get(username)
            await event.respond(reply)

        except ValueError:
            reply = 'Не корректный номер папки'
            await event.respond(reply)
            success = False
    else:
        success = False
    return success


# Обработчик команды stop
async def process_stop_command(event):
    processed = False
    if event.message.message.lower() == "stop":
        reply = 'Прием новых файлов приостановлен...'
        await event.respond(reply)
        processed = True
    return processed


# Обработчик команды start
async def process_start_command(event):
    processed = False
    if event.message.message.lower() == "start":
        reply = 'Прием новых файлов возобновлен...'
        await event.respond(reply)
        processed = True
    return processed


# Обработчик команды restart
async def process_restart_command(event):
    processed = False
    if event.message.message.lower() == "restart":
        reply = 'Перезапуск клиента'
        await event.respond(reply)
        processed = True
    return processed


# Выполнить команду cmd
def cmd_exec_command(command_string):

    try:
        # Команда на смену рабочей директории
        if command_string.lower().startswith('cd'):
            os.chdir(command_string[3:])
            return ''

        # Какая-нибудь другая команда
        out = os.popen(command_string).read().encode('cp1251').decode('cp866')
    except Exception as e:
        return str(e)

    return out


# Взаимодействие с CMD
async def cmd_interact(event):

    # Выполнить команду
    str_out = cmd_exec_command(event.message.message)
    str_out = str_out + '\n' + cmd_exec_command('echo %cd%')

    # Выдать ответ порциями по 4000 знаков
    while len(str_out) > 4000:
        await event.respond(str_out[0:4000])
        str_out = str_out[4001:]
    await event.respond(str_out)
