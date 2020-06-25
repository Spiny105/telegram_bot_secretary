from telethon import TelegramClient, sync

# Вставляем api_id и api_hash
api_id = 1278307
api_hash = 'e93bfc4241e25e8526468498dfc8217a'

client = TelegramClient('session_name', api_id, api_hash)
client.start()

print(client.get_me().stringify())

# Все чаты, на которые мы подписаны
for dialog in client.iter_dialogs():
    print(dialog.title)

messages = client.get_messages('Silly Bot', 1)
for msg in messages:
    client.download_media(message=msg)
# messages = client.get_entity('Silly Bot')
# print(messages)

# from telethon import TelegramClient
#
# api_id = 1278307
# api_hash = 'e93bfc4241e25e8526468498dfc8217a'
# phone_number = '+79046459645'
# ################################################
# channel_username = 'mooseiclimb'
# ################################################
#
# client = TelegramClient('session_name',
#                     api_id,
#                     api_hash)
#
# assert client.connect()
# if not client.is_user_authorized():
#     client.send_code_request(phone_number)
#     me = client.sign_in(phone_number, input('Enter code: '))
#
# # ---------------------------------------
# msgs = client.get_messages(channel_username, limit=10)
# for msg in msgs.data:
#     if msg.media is not None:
#         client.download_media(message=msg)