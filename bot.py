import os
import telebot
from openai import OpenAI

import os
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
OPENROUTER_API_KEY = os.environ.get('OPENROUTER_API_KEY')

bot = telebot.TeleBot(TELEGRAM_TOKEN)
client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=OPENROUTER_API_KEY)

# Словарь для хранения истории диалогов для каждого пользователя
user_histories = {}

# Системная инструкция: задаем роль и стиль общения
SYSTEM_PROMPT = "Ты — полезный и вежливый ИИ-ассистент. Отвечай кратко и по существу на русском языке."

@bot.message_handler(commands=['start', 'clear'])
def start(message):
    # Команда /clear или /start очищает память бота
    user_histories[message.chat.id] = []
    bot.send_message(message.chat.id, "Привет! Я твой ИИ-ассистент. Память очищена. Задай мне вопрос!")

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    chat_id = message.chat.id
    
    if chat_id not in user_histories:
        user_histories[chat_id] = []
        
    # Добавляем сообщение пользователя в историю
    user_histories[chat_id].append({"role": "user", "content": message.text})
    
    # Ограничиваем память: храним только последние 10 сообщений, чтобы бот не тормозил
    if len(user_histories[chat_id]) > 10:
        user_histories[chat_id] = user_histories[chat_id][-10:]

    try:
        # Собираем запрос: системная инструкция + вся история переписки
        messages_to_send = [{"role": "system", "content": SYSTEM_PROMPT}] + user_histories[chat_id]
        
        response = client.chat.completions.create(
            model="qwen/qwen-2.5-72b-instruct", 
            messages=messages_to_send
        )
        reply = response.choices[0].message.content
        
        # Сохраняем ответ бота в историю
        user_histories[chat_id].append({"role": "assistant", "content": reply})
        
        bot.reply_to(message, reply)
    except Exception as e:
        bot.reply_to(message, "Произошла ошибка при обращении к нейросети.")

print("Bot started...")
bot.polling(none_stop=True)