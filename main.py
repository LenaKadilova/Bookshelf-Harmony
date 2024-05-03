import logging
import sqlite3
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


# БД для хранения информации о пользователях и городах, про достопримечательности в которых он спрашивали
def create_database():
    conn = sqlite3.connect('cities.db')
    cursor = conn.cursor()

    cursor.execute("""CREATE TABLE IF NOT EXISTS users_cities (
                        user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_name TEXT,
                        city_id INTEGER,
                        FOREIGN KEY(city_id) REFERENCES cities(city_id)
                    )""")

    cursor.execute("""CREATE TABLE IF NOT EXISTS cities (
                        city_id INTEGER PRIMARY KEY AUTOINCREMENT,
                        city_name TEXT,
                        UNIQUE(city_id)
                    )""")

    cursor.execute("""CREATE TABLE IF NOT EXISTS sights (
                            sight_id INTEGER PRIMARY KEY AUTOINCREMENT,
                            sight_name TEXT, 
                            city_id INTEGER,
                            coords1 DOUBLE,
                            coords2 DOUBLE
                        )""")

    conn.commit()
    conn.close()


# Добавление информации в БД
def add_sights_to_db(name, city, sights_names, sights_coords):
    try:
        conn = sqlite3.connect('cities.db')
        cursor = conn.cursor()

        cursor.execute("SELECT city_id FROM cities WHERE city_name=?",
                       (city,))
        city_id = cursor.fetchone()

        if not city_id:
            cursor.execute("INSERT INTO cities (city_name) VALUES (?)",
                           (city.lower().capitalize(),))
            conn.commit()

            cursor.execute("SELECT city_id FROM cities WHERE city_name=?",
                           (city,))
            city_id = cursor.fetchone()

        cursor.execute("SELECT user_name FROM users_cities WHERE user_name=?", (name,))
        all_names = cursor.fetchall()

        if not all_names:
            cursor.execute("INSERT INTO users_cities (user_name, city_id) VALUES (?, ?)",
                           (name, city_id[0]))
            conn.commit()
        else:
            cursor.execute("UPDATE users_cities SET city_id=? WHERE user_name=?",
                           (city_id[0], name))
            conn.commit()

        for numb in range(len(sights_names)):
            cursor.execute("SELECT sight_id FROM sights WHERE sight_name=? AND city_id=? AND coords1=? AND coords2=?",
                           (sights_names[numb], city_id[0], sights_coords[numb][0], sights_coords[numb][1]))
            same_sights = cursor.fetchall()
            if not same_sights:
                cursor.execute("INSERT INTO sights (sight_name, city_id, coords1, coords2) VALUES (?, ?, ?, ?)",
                               (sights_names[numb], city_id[0], sights_coords[numb][0], sights_coords[numb][1]))
                conn.commit()

    except Exception as ex:
        print(ex)


async def start(update, context):
    # Вывод приветственного сообщения
    await update.message.reply_text(
        "Доброго времени суток тебе, человек)) Я бот-путешественник, и я помогу сделать твою поездку незабываемой!")

    time.sleep(1)

    # Информация о том, что умеет бот
    await update.message.reply_text(
        "Что я умею?\n\nКоманда /weather <название_города> позволяет узнать погоду в указанном городе.\n\nКоманда "
        "/cafes <название_города> дает рекомендации ресторанов в указанном городе.\n\nКоманда /hotels <название_города>"
        " выдает информацию об отелях в указанном городе.\n\nКоманда /sights <название_города> позволяет узнать больше"
        " о достопримечательностях в указанном городе и об их расположении на карте.\n\nКоманда /help напомпит о том, "
        "что я умею.\n\nВАЖНО! Я бот-патриот, поэтому хорошо разбираюсь только в тех городах, которые находятся в "
        "России.")


async def help(update, context):
    # Информация о том, что умеет бот
    await update.message.reply_text(
        "Что я умею?\n\nКоманда /weather <название_города> позволяет узнать погоду в указанном городе.\n\nКоманда "
        "/cafes <название_города> дает рекомендации ресторанов в указанном городе.\n\nКоманда /hotels <название_города>"
        " выдает информацию об отелях в указанном городе.\n\nКоманда /sights <название_города> позволяет узнать больше"
        " о достопримечательностях в указанном городе и об их расположении на карте."
        "\n\nВАЖНО! Я бот-патриот, поэтому хорошо разбираюсь только в тех городах, которые находятся в "
        "России.")


# Сбор информации об отелях
def find_hotels(response):
    hotels = ''
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
    return hotels


# Отели
async def hotels_in_city(update, context):
    try:
        search_api_server = "https://search-maps.yandex.ru/v1/"
        api_key = "dda3ddba-c9ea-4ead-9010-f43fbc15c6e3"

        # Если задан город
        if context.args:
            city = context.args[0]
            search_params = {
                "apikey": api_key,
                "text": "отель+в+" + city,
                "lang": "ru_RU",
                "type": "biz"
            }

            response = requests.get(search_api_server, params=search_params).json()
            await update.message.reply_text('Гостиницы в городе ' + city + '\n' + find_hotels(response))

        # Если город не задан
        else:
            reply_keyboard = [[{"request_location": True, "text": "Где я?"}]]
            markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
            # выводим приветственное сообщение
            await update.message.reply_text(
                f'''Укажите свое местоположение''', reply_markup=markup)
            return 2

    except Exception:
        await update.message.reply_text(
            'Не удалось получить информацию о гостиницах. Проверь название города. Он точно находится в России?')


# Отели по местоположению пользователя
async def get_location_hotels(update, context):
    search_api_server = "https://search-maps.yandex.ru/v1/"
    api_key = "dda3ddba-c9ea-4ead-9010-f43fbc15c6e3"
    current_pos = (update.message.location.latitude, update.message.location.longitude)
    search_params = {
        "apikey": api_key,
        "text": "отель",
        "ll": str(current_pos[1]) + ',' + str(current_pos[0]),
        "lang": "ru_RU",
        "type": "biz"
    }

    response = requests.get(search_api_server, params=search_params).json()
    await update.message.reply_text('Отели недалеко от Вас:\n' + find_hotels(response))

    return ConversationHandler.END


# Сбор информации о ресторанах
def find_cafes(response):
    cnt = 0
    cafes = ''
    for cafe in response['features']:
        cnt += 1
        cafe_name = cafe['properties']['CompanyMetaData'].get('name', '')
        cafe_address = cafe['properties']['CompanyMetaData'].get('address', '')
        cafe_url = cafe['properties']['CompanyMetaData'].get('url', '')
        cafe_hours = cafe['properties']['CompanyMetaData'].get('Hours', '')
        if cafe_hours:
            cafe_hours = cafe_hours.get('text', '')
        else:
            cafe_hours = ''
        if cafe_name:
            cafes += (str(cnt) + ') ' + 'Название: ' + cafe_name + '\n')
            if cafe_address:
                cafes += ('Адрес: ' + cafe_address + '\n')
            if cafe_url:
                cafes += ('Сайт: ' + cafe_url + '\n')
            if cafe_hours:
                cafes += ('График работы: ' + cafe_hours + '\n')
            cafes += '\n'
    return cafes


async def restaurants(update, context):
    try:
        search_api_server = "https://search-maps.yandex.ru/v1/"
        api_key = "dda3ddba-c9ea-4ead-9010-f43fbc15c6e3"
        if context.args:
            city = context.args[0]
            search_params = {
                "apikey": api_key,
                "text": "кафе+в+" + city,
                "lang": "ru_RU",
                "type": "biz"
            }

            response = requests.get(search_api_server, params=search_params).json()

            await update.message.reply_text('Рестораны в городе ' + city + ':\n' + find_cafes(response))

        else:
            reply_keyboard = [[{"request_location": True, "text": "Где я?"}]]
            markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)

            # выводим приветственное сообщение
            await update.message.reply_text(
                f'''Укажите свое местоположение''', reply_markup=markup)

            return 1

    except Exception as ex:
        print(ex)
        await update.message.reply_text(
            'Не удалось получить информацию о ресторанах. Проверь название города. Он точно находится в России?')


async def get_location_cafes(update, context):
    search_api_server = "https://search-maps.yandex.ru/v1/"
    api_key = "dda3ddba-c9ea-4ead-9010-f43fbc15c6e3"
    current_pos = (update.message.location.latitude, update.message.location.longitude)
    search_params = {
        "apikey": api_key,
        "text": "кафе",
        "ll": str(current_pos[1]) + ',' + str(current_pos[0]),
        "lang": "ru_RU",
        "type": "biz"
    }

    response = requests.get(search_api_server, params=search_params).json()
    await update.message.reply_text('Рестораны недалеко от Вас:\n' + find_cafes(response))

    return ConversationHandler.END


async def sights_in_city(update, context):
    try:
        search_api_server = "https://search-maps.yandex.ru/v1/"
        api_key = "dda3ddba-c9ea-4ead-9010-f43fbc15c6e3"
        city = context.args[0]
        name = update.message.from_user.username
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

        cnt = 0
        all_coords = []
        sights_names = []
        sights = 'Достопримечательности в городе ' + city + '\n'
        coords_left = []
        coords_right = []

        for sight in response['features']:
            cnt += 1
            sight_name = sight['properties']['CompanyMetaData'].get('name', '')
            sight_address = sight['properties']['CompanyMetaData'].get('address', '')
            sight_coords = sight['geometry']['coordinates']

            all_coords.append(sight_coords)
            coords_left.append(sight_coords[0])
            coords_right.append(sight_coords[1])

            if sight_name:
                sights += (str(cnt) + ') ' + 'Название: ' + sight_name + '\n')
                sights_names.append(sight_name)
                if sight_address:
                    sights += ('Адрес: ' + sight_address + '\n')
                sights += '\n'

        metks = ''
        req = "http://static-maps.yandex.ru/1.x/?ll=" + str(
            round((min(coords_left) + max(coords_left)) / 2, 6)) + ',' + str(
            round((min(coords_right) + max(coords_right)) / 2, 6)) + '&spn=0.2,0.2&l=map&pt=' + str(
            all_coords[0][0]) + ',' + str(all_coords[0][1]) + ',' + 'pmorl1'
        k = 0

        for coord in all_coords:
            k += 1
            metks += '~' + str(coord[0]) + ',' + str(coord[1]) + ',' + 'pmorl' + str(k)
        req += metks

        with open('im.jpg', 'wb') as f:
            f.write(requests.get(req).content)

        await update.message.reply_text(sights)
        await update.message.reply_photo(photo="im.jpg",
                                         caption='Введи номер/номера достопримечательностей, которые ты хотел бы посетить, через пробел.\nНапример, 1 3 10')

        add_sights_to_db(name, city, sights_names, all_coords)

        return 1

    except Exception as ex:
        print(ex)
        await update.message.reply_text(
            'Не удалось получить информацию о достопримечательностях. Проверь название города. Он точно находится в России?')


async def sights_numbers(update, context):
    numbers = update.message.text.split()
    name = update.message.from_user.username
    conn = sqlite3.connect('cities.db')
    cursor = conn.cursor()

    cursor.execute("SELECT city_id FROM users_cities WHERE user_name=?", (name,))
    city_id = cursor.fetchone()[0]

    cursor.execute("SELECT * FROM sights WHERE city_id=?",
                   (city_id,))
    city_info = cursor.fetchall()

    for number in numbers:
        sight = city_info[int(number) - 1][1]
        req = "http://static-maps.yandex.ru/1.x/?ll=" + str(city_info[int(number) - 1][3]) + ',' + str(
            city_info[int(number) - 1][4]) + '&spn=0.02,0.02&l=map&pt=' + str(
            city_info[int(number) - 1][3]) + ',' + str(city_info[int(number) - 1][4]) + ',' + 'pmorl' + number
        with open('im.jpg', 'wb') as f:
            f.write(requests.get(req).content)
        await update.message.reply_photo(photo="im.jpg",
                                         caption=sight)

    return ConversationHandler.END  # Константа, означающая конец диалога.
    # Все обработчики из states и fallbacks становятся неактивными.


async def stop(update, context):
    await update.message.reply_text("Всего доброго!")
    return ConversationHandler.END


async def weather_response(update, context):
    try:
        # получаем город из сообщения пользователя
        city = context.args[0]
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
    # Создаём объект Application
    application = Application.builder().token(BOT_TOKEN).build()

    # Создаём обработчик сообщений типа filters.TEXT
    # из описанной выше асинхронной функции echo()
    # После регистрации обработчика в приложении
    # эта асинхронная функция будет вызываться при получении сообщения
    # с типом "текст", т. е. текстовых сообщений.

    # Регистрируем обработчик в приложении.

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help))
    application.add_handler(CommandHandler("weather", weather_response))

    conv_handler_sights = ConversationHandler(
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

    application.add_handler(conv_handler_sights)

    conv_handler_cafes = ConversationHandler(
        # Точка входа в диалог.
        # В данном случае — команда /start. Она задаёт первый вопрос.
        entry_points=[CommandHandler('cafes', restaurants)],

        # Состояние внутри диалога.
        # Вариант с двумя обработчиками, фильтрующими текстовые сообщения.
        states={
            # Функция читает ответ на первый вопрос и задаёт второй.
            1: [MessageHandler(filters._Location(), get_location_cafes)]
        },

        # Точка прерывания диалога. В данном случае — команда /stop.
        fallbacks=[CommandHandler('stop', stop)]
    )

    application.add_handler(conv_handler_cafes)

    conv_handler_hotels = ConversationHandler(
        # Точка входа в диалог.
        # В данном случае — команда /start. Она задаёт первый вопрос.
        entry_points=[CommandHandler('hotels', hotels_in_city)],

        # Состояние внутри диалога.
        # Вариант с двумя обработчиками, фильтрующими текстовые сообщения.
        states={
            # Функция читает ответ на первый вопрос и задаёт второй.
            2: [MessageHandler(filters._Location(), get_location_hotels)]
        },

        # Точка прерывания диалога. В данном случае — команда /stop.
        fallbacks=[CommandHandler('stop', stop)]
    )

    application.add_handler(conv_handler_hotels)

    # Запускаем приложение.
    application.run_polling()


# Запускаем функцию main() в случае запуска скрипта.
if __name__ == '__main__':
    create_database()
    main()
