import os

from dotenv import find_dotenv, load_dotenv

if not find_dotenv():
    exit('Переменные окружения не загружены: отсутствует файл .env')
else:
    load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')
API_KEY = os.getenv('API_KEY')
OWNER_ID = os.getenv('OWNER_ID')
DEFAULT_COMMANDS = (
    ('start', 'Запустить бота'),
    ('help', 'Вывести справку'),
    ('lowprice', 'Поиск отелей по цене'),
    ('bestdeal', 'Поиск отелей близких к центру'),
    ('guest_rating', 'Поиск отелей по оценкам'),
    ('get_history', 'Вывод истории')
)