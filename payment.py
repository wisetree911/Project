import logging # для логирования
import requests
import uuid
from yookassa import Configuration, Payment
from yookassa.payment import PaymentResponse
from config import shopId, yookassa_key, bot_url, BOT_TOKEN
import asyncio
logging.basicConfig(level=logging.INFO)


# функция которая отправляет запрос на сервер юкассы через API юкассы
def create_payment(chat_id, amount: str, description=' ') -> PaymentResponse:
    # авторизация в юкассе
    Configuration.account_id = shopId
    Configuration.secret_key = yookassa_key
    # генерирую случайный айди для платежа
    idempotence_key = str(uuid.uuid4())
    # запрос через АПИ юкассы
    try:
        payment = Payment.create(
            {
            "amount": {
                "value": f'{amount}',
                "currency": "RUB"
            },
            "payment_method_data": {
                "type": "bank_card"
            },
            "confirmation": {
                "type": "redirect",
                "return_url": f'{bot_url}'
            },
            'capture': True,
            'metadata': {
                'chat_id': f'{chat_id}'
            },
            "description": f'{idempotence_key}: {description}'
        },
            idempotence_key
        )
    except Exception as e:
        logging.error(f' {chat_id}, {amount} RUB, {idempotence_key} Не удалось получить ответ от Юкассы, ошибка: {e}')
        return
    else:
        logging.info(f' {chat_id}, {amount} RUB, {idempotence_key} Ожидается оплата')
        return payment # через payment в дальнейшем получим ссылку на оплату)


 # асинхронная функция для проверки оплаты (чтобы не блокировать остальной функционал бота)
async def check_payment(payment: PaymentResponse, chat_id: int):
    while payment.status == 'pending':
        await asyncio.sleep(2.5)
        print(payment.status)
        payment = Payment.find_one(payment.id)
    # когда оплата прошла, уведомляем пользователя в чате
    if payment.status == 'succeeded':
        logging.info(f' {chat_id}, Оплата прошла успешно')
        await send_success_message(chat_id, BOT_TOKEN)
        return True
    # если оплата не прошла, уведомляем пользователя
    else:
        logging.warning(f' {chat_id}, Оплата не прошла')
        await send_fail_message(chat_id, BOT_TOKEN)
        return False


# функция для запуска асинхронной проверки статуса платежа
def start_payment_check(payment, chat_id:int)->None:
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    # запускаем функцию check_payment() асинхронно до ее выполнения
    loop.run_until_complete(check_payment(payment, chat_id))


# функция чтобы отправить через бота сообщение об успешной оплате (через requests)
async def send_success_message(chat_id, BOT_TOKEN)->None:
    response = requests.post(f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage', json=
    {
        'chat_id': chat_id,
        'text': 'Оплата прошла успешно!'
    })


# функция чтобы отправить через бота сообщение об успешной оплате (через requests)
async def send_fail_message(chat_id, BOT_TOKEN)->None:
    response = requests.post(f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage', json=
    {
        'chat_id': chat_id,
        'text': 'Оплата не прошла'
    })