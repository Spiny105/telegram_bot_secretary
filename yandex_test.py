# coding=utf-8
import json
import os
import time

import subprocess

# os.chdir('c:\\')
# out = os.popen('echo %cd%').read().encode('cp1251').decode('cp866')
# # print(output.decode('cp866'))
# print(out)

import urllib.parse
try:
    import requests
    import zipfile
    from urllib.parse import urlencode

    # Куда грузить
    dir_for_save = './'

    # Ссылка на файл
    public_key = 'https://yadi.sk/d/ZTpi6EQ8DsHGzA'

    # Базовая ссылка на сервис
    base_url = 'https://cloud-api.yandex.net/v1/disk/public/resources/download?'

    # Получаем загрузочную ссылку
    final_url = base_url + urlencode(dict(public_key=public_key))

    # Отправляем запрос на Яндекс.Диск

    print('Отправка запроса на Яндекс.Диск')
    response = requests.get(final_url)
    print('Статус запроса = ' + str(response.status_code))

    download_url = response.json()['href']
    print('Полученная ссылка для скачивания = ' + download_url)

    # Загружаем файл
    print('Отправка запроса на скачивание файла...')
    download_response = requests.get(download_url)
    print('Статус запроса = ' + str(download_response.status_code))

    # Получаем имя файлам
    print('Получение имени файла...')
    filename = urllib.parse.unquote(download_response.headers.get('Content-Disposition'))[29:]
    print('Имя файла = ' + filename)

    # Загружаем файл
    print('Сохранение файла...')
    with open(dir_for_save + filename, 'wb') as f:
        # Здесь укажите нужный путь к файлу
        f.write(download_response.content)

    # Распаковываем файл
    import os
    import shutil
    import zipfile


    def unpack_zipfile(file, extract_dir, encoding='cp437'):
        with zipfile.ZipFile(file) as archive:
            for entry in archive.infolist():
                name = entry.filename.encode('cp437').decode(encoding)

                if name.startswith('/') or '..' in name:
                    continue

                target = os.path.join(extract_dir, *name.split('/'))
                os.makedirs(os.path.dirname(target), exist_ok=True)
                if not entry.is_dir():  # file
                    with archive.open(entry) as source, open(target, 'wb') as dest:
                        shutil.copyfileobj(source, dest)


    if zipfile.is_zipfile(dir_for_save + filename):
        unpack_zipfile(dir_for_save + filename, r'.', encoding='cp866')

except Exception as e:
    print('ОШИБКА!!!')
    print(str(e))

print('Конец')
input('Для завершения нажмите Enter')
