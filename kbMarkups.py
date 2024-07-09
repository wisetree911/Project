from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton

# клавиатура при /start
def get_start_reply_kb():
    start_reply_kb = ReplyKeyboardMarkup(resize_keyboard=True)
    start_reply_kb.add(KeyboardButton(text="карты"),
                       KeyboardButton(text="оплата"),
                       KeyboardButton(text="картинка"),
                       KeyboardButton(text="получить значение А2 гугл таблицы")
                       )
    return start_reply_kb


# встроенная (в сообщение) клавиатура для оплаты
def get_payment_inline_kb(payment_link: str):
    payment_inline_kb = InlineKeyboardMarkup()
    payment_inline_kb.add(InlineKeyboardButton(text='Перейти', url=payment_link))
    return payment_inline_kb