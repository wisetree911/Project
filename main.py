import logging # для логирования
import telebot
from telebot.types import Message
from config import BOT_TOKEN # в config хранятся все ключи
from payment import create_payment, start_payment_check # в payment работа с API юкассы
from kbMarkups import get_start_reply_kb, get_payment_inline_kb # в kbMarkups хранятся клавиатуры
from threading import Thread
from google_tables import get_cell_value, add_to_table_A2 # в google_tables работа с gspread
import datetime

# авторизируемся по токену телеграм бота
bot = telebot.TeleBot(BOT_TOKEN)
logging.basicConfig(level=logging.INFO)


# обработчик для сообщения "оплата"
@bot.message_handler(func=lambda msg: msg.text == 'оплата')
def oplata(msg: Message) -> None:
    logging.info(f'User: {msg.from_user.id} - оплата')
    # создаем запрос на оплату с помощью функции "create_payment()"
    payment = create_payment(msg.chat.id, '2.00')
    #отправляем пользователю ссылку на оплату payment.confirmation.confirmation_url
    try:
        bot.send_message(msg.chat.id, 'Перейдите по ссылке для оплаты', reply_markup=get_payment_inline_kb(payment_link=payment.confirmation.confirmation_url))
        check_thread = Thread(target=start_payment_check, args=(payment, msg.chat.id)) # создание и запуск потока для асинхронной проверки оплаты
        check_thread.start()
    except Exception as e:
        logging.error(f'User {msg.from_user.id} Не удалось отправить ссылку на оплату, ошибка: {e}')


# обработчик для команды "start"
@bot.message_handler(commands=['start'])
def welcome(msg: Message) -> None:
    logging.info(f' user: {msg.from_user.id} - /start')
    # после команды старт отправляется приветственное сообщение и появляется клавиатура
    bot.send_message(msg.chat.id, text='Стартовое меню', reply_markup=get_start_reply_kb()) # отправка клавиатуры при команде /start


# обработчик для сообщения "карты"
@bot.message_handler(func = lambda msg: msg.text == 'карты')
def send_map(msg: Message) -> None:
    logging.info(f' user: {msg.from_user.id} - карты')
    # отрпавляем точку на карте по ширине и долготе
    bot.send_location(msg.chat.id, longitude=55.943968, latitude=54.719721)


# обработчик для сообщения "картинка"
@bot.message_handler(func = lambda msg: msg.text == 'картинка')
def send_pic(msg: Message) -> None:
    logging.info(f' user: {msg.from_user.id} - картинка')
    # отправляем картинку 'image1.jpg'
    img = open('media//image1.jpg', 'rb')
    bot.send_photo(msg.chat.id, photo=img, caption="Вот ваше изображение")


# обработчик для сообщения "получить значение А2 гугл таблицы"
@bot.message_handler(func=lambda msg: msg.text == 'получить значение А2 гугл таблицы')
def get_google_table(msg: Message) -> None:
    logging.info(f' user: {msg.from_user.id} - получить значение А2 гугл таблицы')
    value = get_cell_value(2, 1)
    bot.send_message(msg.chat.id, f'Значение таблицы в ячейке А2 {repr(value)}')


# обработчик для всего остального текста (то есть, все даты попадают в него)
@bot.message_handler(content_types=['text'])
def date_check(msg: Message):
    logging.info(f' user: {msg.from_user.id} - {msg.text}')
    input_date = msg.text
    # проверяем дату на корректность по форме "%d.%m.%y"
    try:
        datetime.datetime.strptime(input_date, "%d.%m.%y")
        logging.info(f' user: {msg.from_user.id} - дата корректна')
    except ValueError:
        bot.send_message(msg.chat.id, "дата неверна")
        logging.info(f' user: {msg.from_user.id} - дата некорректна')
    else:
        # если дата корректна, то добавляем ее в гугл таблицу в столбец В
        add_to_table_A2(input_date)
        bot.send_message(msg.chat.id, "дата верна")

# запуск бота
if __name__ == '__main__':
    try:
        bot.infinity_polling()
    except Exception as e:
        logging.error(f' Ошибка при запуске бота {e}')
