from typing import List
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton



def create_reply_keyboard(items: List[str], row_width: int = 3) -> ReplyKeyboardMarkup:
    """
    Создание reply клавиатуры
    Creation of reply keyboard
    """
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    row = []
    for i, item in enumerate(items, 1):
        row.append(KeyboardButton(text=item))
        if i % row_width == 0:
            keyboard.row(*row)
            row = []
    if row:
        keyboard.row(*row)
    return keyboard