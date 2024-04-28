import logging
# Запускаем логгирование
from telegram.ext import Application, MessageHandler, filters, CommandHandler, ConversationHandler
from config import BOT_TOKEN

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)


async def start(update, context):
    await update.message.reply_text(
        "Привет. Пройдите небольшой опрос, пожалуйста!\n"
        "Вы можете прервать опрос, послав команду /stop.\n"
        "В каком городе вы живёте?")

    # Число-ключ в словаре states —
    # втором параметре ConversationHandler'а.
    return 1


async def first_response(update, context):
    # Сохраняем ответ в словаре.
    data = update.message.text
    print(data)
    if data == '/skip':
        await update.message.reply_text(
            f"Какая погода у вас за окном?")
    else:
        context.user_data['locality'] = update.message.text
        await update.message.reply_text(
            f"Какая погода в городе {context.user_data['locality']}?")
    return 2


# Добавили словарь user_data в параметры.
async def second_response(update, context):
    weather = update.message.text
    logger.info(weather)
    # Используем user_data в ответе.
    if context.user_data.get('locality'):
        await update.message.reply_text(
            f"Спасибо за участие в опросе! Привет, {context.user_data['locality']}!")
        context.user_data.clear()  # очищаем словарь с пользовательскими данными
    else:
        await update.message.reply_text(
            f"Спасибо за участие в опросе!")
    return ConversationHandler.END


async def stop(update, context):
    await update.message.reply_text("Всего доброго!")
    return ConversationHandler.END


def main():
    # Создаём объект Application.
    # Вместо слова "TOKEN" надо разместить полученный от @BotFather токен
    application = Application.builder().token(BOT_TOKEN).build()
    conv_handler = ConversationHandler(
        # Точка входа в диалог.
        # В данном случае — команда /start. Она задаёт первый вопрос.
        entry_points=[CommandHandler('start', start)],

        # Состояние внутри диалога.
        # Вариант с двумя обработчиками, фильтрующими текстовые сообщения.
        states={
            # Функция читает ответ на первый вопрос и задаёт второй.
            1: [MessageHandler(filters.TEXT, first_response)],
            # Функция читает ответ на второй вопрос и завершает диалог.
            2: [MessageHandler(filters.TEXT & ~filters.COMMAND, second_response)]
        },

        # Точка прерывания диалога. В данном случае — команда /stop.
        fallbacks=[CommandHandler('stop', stop)]
    )

    application.add_handler(conv_handler)
    application.run_polling()


if __name__ == '__main__':
    main()
