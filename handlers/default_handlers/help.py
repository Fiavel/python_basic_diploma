from telebot.types import Message

from loader import bot, config


@bot.message_handler(commands=['help'])
def bot_help(message: Message):
    """response to command /help, which gives all the commands and provides their descriptions"""
    if len(config.OWNER_ID) > 0:
        bot.send_message(config.OWNER_ID,' Кто-то использовал команду: /help')
    text = ('Список команд:\n'
            '/start - Начать диалог.\n'
            '/help - Получить справку.\n'
            '/bestdeal - Найти ближайшие к центру города отеля.\n'
            '/guest_rating - Найти лучшие по оценкам пользователей отели.\n'
            '/lowprice - Найти самые доступные отели.\n'
            '/get_history - Посмотреть историю поиска.'
            )

    bot.send_message(message.from_user.id, ''.join(text))