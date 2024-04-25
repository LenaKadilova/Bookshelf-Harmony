import requests
import logging
import random

from telegram.ext import Application, MessageHandler, filters, CommandHandler
BOT_TOKEN = '6537556714:AAGIdslrTde82frSh8TtbIWG3SyuACW0anY'
import time
from telegram import ReplyKeyboardMarkup

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)


async def start(update, context):
    await update.message.reply_text(f"Привет! Введите название города чтобы получить список гостиниц.")


async def hotels_in_city(update, context):
    try:
        city = context.args[0]
        print(city)
        search_api_server = "https://search-maps.yandex.ru/v1/"
        api_key = "dda3ddba-c9ea-4ead-9010-f43fbc15c6e3"

        search_params = {
            "apikey": api_key,
            "text": "отель+в+" + city,
            "lang": "ru_RU",
            "type": "biz"
        }

        response = requests.get(search_api_server, params=search_params).json()
        print(response)

        hotels = 'Гостиницы в городе ' + city + '\n'
        cnt = 0
        for hotel in response['features']:
            cnt += 1
            hotel_name = hotel['properties']['CompanyMetaData'].get('name', '')
            hotel_address = hotel['properties']['CompanyMetaData'].get('address', '')
            hotel_url = hotel['properties']['CompanyMetaData'].get('url', '')
            if hotel_name:
                hotels += (str(cnt) + ') ' + 'Название: ' + hotel_name + '\n')
                if hotel_address:
                    hotels += ('Адрес: ' + hotel_address + '\n')
                if hotel_url:
                    hotels += ('Сайт: ' + hotel_url + '\n')
                hotels += '\n'
        await update.message.reply_text(hotels)
    except Exception:
        await update.message.reply_text('Не удалось получить информацию о гостиницах.')


async def restaurants(update, context):
    try:
        search_api_server = "https://search-maps.yandex.ru/v1/"
        api_key = "dda3ddba-c9ea-4ead-9010-f43fbc15c6e3"

        address_ll = "37.588392,55.734036"

        search_params = {
            "apikey": api_key,
            "text": "кафе",
            "lang": "ru_RU",
            "ll": address_ll,
            "type": "biz"
        }

        response = requests.get(search_api_server, params=search_params).json()
        cnt = 0
        cafes = 'Рестораны недалеко от Вас:\n'
        for cafe in response['features']:
            cnt += 1
            cafe_name = cafe['properties']['CompanyMetaData'].get('name', '')
            cafe_address = cafe['properties']['CompanyMetaData'].get('address', '')
            cafe_url = cafe['properties']['CompanyMetaData'].get('url', '')
            cafe_hours = cafe['properties']['CompanyMetaData'].get('Hours', '').get('text', '')
            if cafe_name:
                cafes += (str(cnt) + ') ' + 'Название: ' + cafe_name + '\n')
                if cafe_address:
                    cafes += ('Адрес: ' + cafe_address + '\n')
                if cafe_url:
                    cafes += ('Сайт: ' + cafe_url + '\n')
                if cafe_hours:
                    cafes += ('График работы: ' + cafe_hours + '\n')
                cafes += '\n'
        await update.message.reply_text(cafes)
    except Exception:
        await update.message.reply_text('Не удалось получить информацию о ресторанах.')


def main():
    # Создаём объект Application.
    # Вместо слова "TOKEN" надо разместить полученный от @BotFather токен
    application = Application.builder().token(BOT_TOKEN).build()

    # Создаём обработчик сообщений типа filters.TEXT
    # из описанной выше асинхронной функции echo()
    # После регистрации обработчика в приложении
    # эта асинхронная функция будет вызываться при получении сообщения
    # с типом "текст", т. е. текстовых сообщений.
    # text_handler = MessageHandler(filters.TEXT, start)

    # Регистрируем обработчик в приложении.

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("hotels", hotels_in_city))
    application.add_handler(CommandHandler("restaurants", restaurants))
    # application.add_handler(text_handler)

    # Запускаем приложение.
    application.run_polling()


# Запускаем функцию main() в случае запуска скрипта.
if __name__ == '__main__':
    main()
