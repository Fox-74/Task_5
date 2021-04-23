import requests
import telebot
from config import telegram_token

state = 0

bot = telebot.TeleBot(telegram_token, parse_mode=None)
kb = telebot.types.ReplyKeyboardMarkup(True)
kb.row('/show_news')
kb.row('Добавить категорию', 'Добавить ключевое слово')
kb.row('Просмотр категорий', 'Просмотр ключевых слов')
kb.row('Удалить категорию', 'Удалить ключевое слово')


@bot.message_handler(commands=['start'])
def send_start(inp):
    a = requests.get(f'http://127.0.0.1:8080/users/{inp.from_user.id}')
    print(a.json())
    bot.reply_to(inp, f"Добрый день {inp.from_user.first_name}!\n Желаете посмотреть новости?", reply_markup=kb)

@bot.message_handler(commands=['show_news'])
def get_news(inp):
    a = requests.get('http://127.0.0.1:8080/news/')
    for i in range(len(a.json()['link'])):
        bot.reply_to(inp, (a.json()['link'][i]), reply_markup=kb)


@bot.message_handler(content_types=["text"])
def main(inp):
    global state

    if state == 1:
        print(inp.text)
        requests.put(f'http://127.0.0.1:8080/subscriptions/categories/{inp.text}')
        state = 0
    elif state == 2:
        print(inp.text)
        requests.put(f'http://127.0.0.1:8080/subscriptions/keywords/{inp.text}')
        state = 0
    elif state == 5:
        requests.delete(f'http://127.0.0.1:8080/subscriptions/categories/{inp.text}')
        state = 0
    elif state == 6:
        requests.delete(f'http://127.0.0.1:8080/subscriptions/keywords/{inp.text}')
        state = 0

    bot.send_message(inp.chat.id, 'Ok', reply_markup=kb)
    if inp.text == "Добавить категорию":
        state = 1
        keyboard1 = telebot.types.ReplyKeyboardMarkup(True)
        keyboard1.row('sports', 'business')
        keyboard1.row('entertainment', 'general')
        keyboard1.row('health', 'science')
        keyboard1.row('technology')
        bot.send_message(inp.chat.id, "Доступные категории", reply_markup=keyboard1)
    elif inp.text == 'Добавить ключевое слово':
        state = 2
        bot.send_message(inp.chat.id, "Введите ключевое слово")
    elif inp.text == 'Просмотр категорий':
        a = requests.get(f'http://127.0.0.1:8080/subscriptions/categories/{1}')
        bot.send_message(inp.chat.id, f"{a.json()}")
    elif inp.text == 'Просмотр ключевых слов':
        a = requests.get(f'http://127.0.0.1:8080/subscriptions/keywords/{1}')
        bot.send_message(inp.chat.id, f"{a.json()}")
    elif inp.text == 'Удалить категорию':
        state = 5
        bot.send_message(inp.chat.id, "Введите категорию для удаления из подписки")
    elif inp.text == 'Удалить ключевое слово':
        state = 6
        bot.send_message(inp.chat.id, "Введите ключевое слово для удаления из подписки")


bot.polling()