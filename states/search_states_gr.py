from telebot.handler_backends import State, StatesGroup


class SearchFilterState(StatesGroup):
    city_gr = State()
    corrections_gr = State()
    arrival_date_gr = State()
    deport_date_gr = State()
    price_range_gr = State()
    result_gr = State()