from telebot.handler_backends import State, StatesGroup


class SearchFilterState(StatesGroup):
    city_bd = State()
    corrections_bd = State()
    arrival_date_bd = State()
    deport_date_bd = State()
    price_range_bd = State()
    result_bd = State()