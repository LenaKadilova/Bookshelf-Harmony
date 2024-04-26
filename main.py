import requests
import logging
import random
import time
import json
from telegram import ReplyKeyboardMarkup
from telegram.ext import Application, MessageHandler, filters, CommandHandler, Updater
from config import BOT_TOKEN
import requests
import json

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)



async def start(update, context):
    await update.message.reply_text(
        "Доброго времени суток тебе, человек)) Я бот-путешественник, и я помогу сделать твою поездку незабываемой!")
    time.sleep(1)
    await update.message.reply_text(
        "Что я умею?\nКоманда /weather <название_города> позволяет узнать погоду в указанном городе.\nКоманда /cafes <название_города> дает рекомендации ресторанов в указанном городе.\nКоманда /hotels <название_города> выдает информацию об отелях в указанном городе.\nКоманда /sights <название_города> узнать больше о достопримечательностях в указанном городе и об их расположении на карте.")


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
        city = context.args[0]

        search_params = {
            "apikey": api_key,
            "text": "кафе+в+" + city,
            "lang": "ru_RU",
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


async def sights_in_city(update, context):
    try:
        search_api_server = "https://search-maps.yandex.ru/v1/"
        api_key = "dda3ddba-c9ea-4ead-9010-f43fbc15c6e3"
        city = context.args[0]

        search_params = {
            "apikey": api_key,
            "text": "достопримечательности+в+" + city,
            "lang": "ru_RU",
            "type": "biz"
        }

        response = requests.get(search_api_server, params=search_params).json()
        with open('jsons.json', 'w') as f:
            json.dump(response, f, indent=4)
        print(response)
        cnt = 0
        all_coords = []
        sights = 'Достопримечательности в городе ' + city + '\n'
        for sight in response['features']:
            cnt += 1
            sight_name = sight['properties']['CompanyMetaData'].get('name', '')
            sight_address = sight['properties']['CompanyMetaData'].get('address', '')
            sight_coords = sight['geometry']['coordinates']
            # all_coords.append(','.join([str(i) for i in sight_coords[::-1]]))
            all_coords.append(sight_coords)
            if sight_name:
                sights += (str(cnt) + ') ' + 'Название: ' + sight_name + '\n')
                if sight_address:
                    sights += ('Адрес: ' + sight_address + '\n')
                sights += '\n'
        # all_coords = ','.join(all_coords)
        print(all_coords)
        metks = ''
        req = "http://static-maps.yandex.ru/1.x/?ll=" + str(all_coords[0][0]) + ',' + str(all_coords[0][1]) + '&spn=0.08,0.08&l=sat&pt=' + str(all_coords[0][0]) + ',' + str(all_coords[0][1]) + ',' + 'pmorl1'
        k = 0
        print(all_coords)
        for coord in all_coords:
            k += 1
            metks += '~' + str(coord[0]) + ',' + str(coord[1]) + ',' + 'pmorl' + str(k)
        req += metks

        with open('im.png', 'wb') as f:
            f.write(requests.get(req).content)
        await update.message.reply_text(sights)
        # await update.message.send_photo(photo="im.png", caption="hello test123")
    except Exception as ex:
        print(ex)
        await update.message.reply_text('Не удалось получить информацию о ресторанах.')


async def weather_response(update, context):
    # await update.message.reply_text("Тут могла бы быть погода")
    try:
        # получаем город из сообщения пользователя
        city = context.args[0]
        print(city)
        # формируем запрос и отправляем его на сервер
        url = 'https://api.openweathermap.org/data/2.5/weather?q=' + city + '&units=metric&lang=ru&appid=79d1ca96933b0328e1c7e3e7a26cb347'
        weather_data = requests.get(url).json()

        temperature = round(weather_data['main']['temp'])
        temperature_feels = round(weather_data['main']['feels_like'])
        # формируем ответы
        t_now = 'Сейчас в городе ' + city + ' ' + str(temperature) + ' °C.'
        t_feels = 'Ощущается как ' + str(temperature_feels) + ' °C.'
        t_desc = 'В городе ' + city + ' сейчас ' + weather_data['weather'][0]['description'] + '.'
        await update.message.reply_text(t_now + '\n' + t_feels + '\n' + t_desc)
    except Exception:
        await update.message.reply_text("Проверьте название города!")


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
    application.add_handler(CommandHandler("cafes", restaurants))
    application.add_handler(CommandHandler("sights", sights_in_city))
    application.add_handler(CommandHandler("weather", weather_response))
    # application.add_handler(text_handler)

    # Запускаем приложение.
    application.run_polling()


# Запускаем функцию main() в случае запуска скрипта.
if __name__ == '__main__':
    main()
