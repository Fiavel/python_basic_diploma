from telebot.types import Message

from loader import bot, config

@bot.message_handler(commands=['start'])
def bot_start(message:Message):
    """response to command /start with most of useful commands and their descriptions"""
    if len(config.OWNER_ID) > 0:
        bot.send_message(config.OWNER_ID,' Кто-то использовал команду: /start')
    bot.set_state(message.from_user.id, state=None)
    bot.send_message(message.from_user.id, 'Привет {}!\nВ этом боте можно найти отели в разных городах и странах\n'
                          'Воспользуйся командами:\n/lowprice - для поиска самых доступных отелей\n'
                          '/guest_rating - для поиска по популярности\n/bestdeal - для поиска отелей,'
                          'ближе всего находящимся к центру'
                 .format(message.from_user.full_name))