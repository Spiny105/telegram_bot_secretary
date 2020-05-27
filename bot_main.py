import telebot;

secret_token = '1163165731:AAFLt3bHNfohz-ulY8kU_0VVgBny5Vr4EkA'

bot = telebot.TeleBot(secret_token);

@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    if message.text == "Привет":
        bot.send_message(message.from_user.id, "А мама мне говорила, что я красивый :З")
    elif message.text == "/help":
        bot.send_message(message.from_user.id, "Напиши \'Привет\'")
    else:
        bot.send_message(message.from_user.id, "Я тупой бот и я тебя не понимаю. Напиши /help.")
        
@bot.message_handler(content_types=['document'])
def handle_file(message):
    try:
        chat_id = message.chat.id
        file_info = bot.get_file(message.document.file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        src = r'C:\Users\Nikolay\OneDrive\Документы\py_bot\\' + message.document.file_name;
        with open(src, 'wb') as new_file:
            new_file.write(downloaded_file)
        bot.reply_to(message, "Пожалуй, я сохраню это")
    except Exception as e:
        bot.reply_to(message, e)
        

bot.polling(none_stop=True, interval=0)