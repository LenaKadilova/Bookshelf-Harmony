import requests
import logging
import random

from telegram.ext import Application, MessageHandler, filters, CommandHandler
from config import BOT_TOKEN
import time
from telegram import ReplyKeyboardMarkup

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)


async def start(update, context):
    await update.message.reply_text(f"Привет! Введите название города чтобы получить список гостиниц.")


async def hotels_in_city(update, context):
    city = update.message.text
    api_key = "dda3ddba-c9ea-4ead-9010-f43fbc15c6e3"
    url = f'https://search-maps.yandex.ru/v1/?api_key={api_key}&text=гостиницы+в+{city}&type=biz&lang=ru_RU'
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        hotels = [item['properties']['CompanyMetaData']['name'] for item in data['features']]
        hotels_list = '\n'.join(hotels)

        await update.message.reply_text(f'Гостиницы в городе {city}:\n{hotels_list}')
    else:
        await update.message.reply_text('Не удалось получить информацию о гостиницах.')


def main():
    # Создаём объект Application.
    # Вместо слова "TOKEN" надо разместить полученный от @BotFather токен
    application = Application.builder().token(BOT_TOKEN).build()

    # Создаём обработчик сообщений типа filters.TEXT
    # из описанной выше асинхронной функции echo()
    # После регистрации обработчика в приложении
    # эта асинхронная функция будет вызываться при получении сообщения
    # с типом "текст", т. е. текстовых сообщений.
    text_handler = MessageHandler(filters.TEXT, start)

    # Регистрируем обработчик в приложении.

    application.add_handler(CommandHandler("start", start))
    application.add_handler(text_handler)

    # Запускаем приложение.
    application.run_polling()


# Запускаем функцию main() в случае запуска скрипта.
if __name__ == '__main__':
    main()
