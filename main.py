import logging
import random
import time
from telegram import ReplyKeyboardMarkup
from telegram.ext import Application, MessageHandler, filters, CommandHandler, Updater, ConversationHandler
from config import BOT_TOKEN
import requests
import json

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)
all_coords = []


async def start(update, context):
    await update.message.reply_text(
        "Доброго времени суток тебе, человек)) Я бот-путешественник, и я помогу сделать твою поездку незабываемой!")
    time.sleep(1)
    await update.message.reply_text(
        "Что я умею?\n\nКоманда /weather <название_города> позволяет узнать погоду в указанном городе.\n\nКоманда /cafes <название_города> дает рекомендации ресторанов в указанном городе.\n\nКоманда /hotels <название_города> выдает информацию об отелях в указанном городе.\n\nКоманда /sights <название_города> позволяет узнать больше о достопримечательностях в указанном городе и об их расположении на карте.\n\nВАЖНО! Я бот-патриот, поэтому хорошо разбираюсь только в тех городах, которые находятся в России.")


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
        await update.message.reply_text(
            'Не удалось получить информацию о гостиницах. Проверь название города. Он точно находится в России?')


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
        await update.message.reply_text(
            'Не удалось получить информацию о ресторанах. Проверь название города. Он точно находится в России?')


async def sights_in_city(update, context):
    print(555)
    global all_coords
    print(66)
    try:
        search_api_server = "https://search-maps.yandex.ru/v1/"
        api_key = "dda3ddba-c9ea-4ead-9010-f43fbc15c6e3"
        print(context.args)
        city = context.args[0]
        # city = 'Чебоксары'
        print(context)

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
        coords_left = []
        coords_right = []
        for sight in response['features']:
            cnt += 1
            sight_name = sight['properties']['CompanyMetaData'].get('name', '')
            sight_address = sight['properties']['CompanyMetaData'].get('address', '')
            sight_coords = sight['geometry']['coordinates']
            # all_coords.append(','.join([str(i) for i in sight_coords[::-1]]))
            all_coords.append(sight_coords)
            coords_left.append(sight_coords[0])
            coords_right.append(sight_coords[1])
            if sight_name:
                sights += (str(cnt) + ') ' + 'Название: ' + sight_name + '\n')
                if sight_address:
                    sights += ('Адрес: ' + sight_address + '\n')
                sights += '\n'
        # all_coords = ','.join(all_coords)
        print(all_coords)
        metks = ''
        req = "http://static-maps.yandex.ru/1.x/?ll=" + str(
            round((min(coords_left) + max(coords_left)) / 2, 6)) + ',' + str(
            round((min(coords_right) + max(coords_right)) / 2, 6)) + '&spn=0.2,0.2&l=map&pt=' + str(
            all_coords[0][0]) + ',' + str(all_coords[0][1]) + ',' + 'pmorl1'
        k = 0
        print(req)
        print(all_coords)
        for coord in all_coords:
            k += 1
            metks += '~' + str(coord[0]) + ',' + str(coord[1]) + ',' + 'pmorl' + str(k)
        req += metks
        print(sights)
        with open('im.jpg', 'wb') as f:
            f.write(requests.get(req).content)
        print(7)
        # await update.message.reply_text(sights)
        print(len(sights))
        # await update.message.reply_photo(photo="im.jpg", caption=sights[:1025])
        await update.message.reply_text(sights)
        await update.message.reply_photo(photo="im.jpg",
                                         caption='Введи номер/номера достопримечательностей, которые ты хотел бы посетить, через пробел.\nНапример, 1 3 10')

        return 1

    except Exception as ex:
        print(ex)
        await update.message.reply_text(
            'Не удалось получить информацию о достопримечательностях. Проверь название города. Он точно находится в России?')


async def sights_numbers(update, context):
    print(11111)
    numbers = update.message.text.split()
    global all_coords

    for number in numbers:
        req = "http://static-maps.yandex.ru/1.x/?ll=" + str(all_coords[int(number) - 1][0]) + ',' + str(
            all_coords[int(number) - 1][1]) + '&spn=0.02,0.02&l=map&pt=' + str(
            all_coords[int(number) - 1][0]) + ',' + str(all_coords[int(number) - 1][1]) + ',' + 'pmorl' + number

        with open('im.jpg', 'wb') as f:
            f.write(requests.get(req).content)
        await update.message.reply_photo(photo="im.jpg",
                                         caption='тут могло бы быть название достопримечательности, но я хочу спать')

    return ConversationHandler.END  # Константа, означающая конец диалога.
    # Все обработчики из states и fallbacks становятся неактивными.


async def stop(update, context):
    await update.message.reply_text("Всего доброго!")
    return ConversationHandler.END


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
    except Exception as ex:
        print(ex)
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
    # text_handler = MessageHandler(filters.TEXT, sights_in_city)

    # Регистрируем обработчик в приложении.

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("hotels", hotels_in_city))
    application.add_handler(CommandHandler("cafes", restaurants))
    application.add_handler(CommandHandler("weather", weather_response))
    # application.add_handler(text_handler)

    conv_handler = ConversationHandler(
        # Точка входа в диалог.
        # В данном случае — команда /start. Она задаёт первый вопрос.
        entry_points=[CommandHandler('sights', sights_in_city)],

        # Состояние внутри диалога.
        # Вариант с двумя обработчиками, фильтрующими текстовые сообщения.
        states={
            # Функция читает ответ на первый вопрос и задаёт второй.
            1: [MessageHandler(filters.TEXT & ~filters.COMMAND, sights_numbers)]
        },

        # Точка прерывания диалога. В данном случае — команда /stop.
        fallbacks=[CommandHandler('stop', stop)]
    )

    application.add_handler(conv_handler)

    # Запускаем приложение.
    application.run_polling()


# Запускаем функцию main() в случае запуска скрипта.
if __name__ == '__main__':
    main()


