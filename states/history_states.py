from telebot.handler_backends import State, StatesGroup

class GetHistoryStates(StatesGroup):
    date = State()
    buttons = State()
    result = State()