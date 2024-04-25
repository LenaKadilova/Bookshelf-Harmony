import logging

import requests
from telegram.ext import Application, MessageHandler, filters, CommandHandler, ConversationHandler, CallbackContext
from telegram import ReplyKeyboardMarkup
BOT_TOKEN = '6537556714:AAGIdslrTde82frSh8TtbIWG3SyuACW0anY'

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)


async def start(update, context):
    reply_keyboard = [[{"request_location": True, "text": "Где я нахожусь"}]]
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    # выводим приветственное сообщение
    await update.message.reply_text(
        f'''Привет! Это бот, который сделает твои путешествия приятнее) 
Перед началом работы укажите свое местоположение''', reply_markup=markup)
    current_pos = (update.message.location.latitude, update.message.location.longitude)
    print(current_pos)


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
        t_now = 'Сейчас в городе ' + city + ' ' + str(temperature) + ' °C'
        t_feels = 'Ощущается как ' + str(temperature_feels) + ' °C'
        await update.message.reply_text(t_now)
        await update.message.reply_text(t_feels)
    except:
        await update.message.reply_text("Проверьте название города!")


async def bot_help(update, context):
    await update.message.reply_text(
        "Команда /weather <название_города> позволяет узнать погоду в указанном городе.")
    await update.message.reply_text(
        "Команда /cafe <название_города> позволяет узнать погоду в указанном городе.")


async def stop(update, context):
    await update.message.reply_text("Всего доброго!")
    return ConversationHandler.END


def main():
    # Создаём объект Application.
    application = Application.builder().token(BOT_TOKEN).build()
    '''conv_handler = ConversationHandler(
        # Точка входа в диалог.
        # В данном случае — команда /start. Она задаёт первый вопрос.
        entry_points=[CommandHandler('start', start)],

        # Состояние внутри диалога.
        # Вариант с двумя обработчиками, фильтрующими текстовые сообщения.
        states={
            # Функция читает ответ на первый вопрос и задаёт второй.
            1: [MessageHandler(filters.TEXT, weather_response)]
        },

        # Точка прерывания диалога. В данном случае — команда /stop.
        fallbacks=[CommandHandler('stop', stop)]
    )'''
    # location_handler = MessageHandler(filters._Location, location)
    # application.add_handler(location_handler)
    application.add_handler(CommandHandler("stop", stop))
    application.add_handler(CommandHandler("weather", weather_response))
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", bot_help))
    '''application.add_handler(conv_handler)'''
    application.run_polling()


if __name__ == '__main__':
    main()
