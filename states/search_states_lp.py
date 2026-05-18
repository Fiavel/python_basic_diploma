from telebot.handler_backends import State, StatesGroup


class SearchFilterState(StatesGroup):
    city_lp = State()
    corrections_lp = State()
    arrival_date_lp = State()
    deport_date_lp = State()
    price_range_lp = State()
    result_lp = State()
