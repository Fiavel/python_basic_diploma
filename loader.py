from telebot import TeleBot
from telebot.storage import StateMemoryStorage
from config_data import config
from utils import bot_db


bot_db.init_database()
storage = StateMemoryStorage()
bot = TeleBot(token=config.BOT_TOKEN, state_storage=storage)
