from telebot.types import BotCommand
from config_data.config import DEFAULT_COMMANDS

def set_default_commands(bot):
    """sets default commands for bot, like /start or /help"""
    bot.set_my_commands(
        [BotCommand(*i) for i in DEFAULT_COMMANDS]
    )