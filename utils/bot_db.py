import datetime
from peewee import SqliteDatabase, Model, IntegerField, TextField, TimestampField

db = SqliteDatabase('bot_history.db')

class SearchHistory(Model):
    user_id = IntegerField()
    query = TextField()
    timestamp = TimestampField(default=datetime.datetime.now)

    class Meta:
        database = db

def init_database():
    """
    Инициализация базы данных
    Initialization for data base
    """
    db.connect()
    db.create_tables([SearchHistory])

def add_search_history(user_id: int, query: list[dict[str, str]]) -> None:
    """
    Добавляет запись в историю поиска
    Adds note to search history
    """
    SearchHistory.create(user_id=user_id, query=str(query))