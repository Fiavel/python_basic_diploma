import datetime
from telebot.types import Message, CallbackQuery
from loader import bot, config
from states.search_states_bd import SearchFilterState
from telegram_bot_calendar import DetailedTelegramCalendar
from utils import api_progress, bot_db, countries_db, keyboard_util



@bot.message_handler(commands=['bestdeal'])
def bestdeal(message: Message) -> None:
    """/bestdeal command handler, which requires sending a message with needed city name and notifies owner of its usage(optional)"""
    if len(config.OWNER_ID) > 0:
        bot.send_message(config.OWNER_ID, ' Кто-то использовал команду: /bestdeal')
    bot.set_state(message.from_user.id, SearchFilterState.city_bd, message.chat.id)
    bot.send_message(message.from_user.id, f'Здравствуйте {message.from_user.username}, введите город назначения')


@bot.message_handler(state=SearchFilterState.city_bd)
def get_city(message: Message) -> None:
    """
    Message handler which processes city name and searches the city in database,
    and asks user to choose the correct city
    """
    if message.text.startswith('/'):
        bot.set_state(message.from_user.id, None)
        bot.send_message(message.from_user.id, 'Воспользуйтесь командой ещё раз')
        return
    loading = bot.send_message(message.from_user.id, 'Поиск...')
    try:
        city_name = countries_db.find_city_and_country_exact(message.text)

        if len(city_name) < 1:
            bot.send_message(message.from_user.id,
                             f'Город: {message.text} не найден!\nУбедитесь в правильности написания\n'
                             f'Или напишите название на английском языке')
            bot.delete_message(chat_id=loading.chat.id, message_id=loading.message_id)
        else:
            bot.set_state(message.from_user.id, SearchFilterState.corrections_bd, message.chat.id)

            keyboard = keyboard_util.create_reply_keyboard(
                city_name.split('\n')
            )
            bot.send_message(message.from_user.id, "Выберите:", reply_markup=keyboard)
            bot.delete_message(chat_id=loading.chat.id, message_id=loading.message_id)
            bot.set_state(message.from_user.id, SearchFilterState.corrections_bd, message.chat.id)


    except RuntimeError:
        bot.send_message(message.from_user.id,
                         f'Город: {message.text} не найден!\nУбедитесь в правильности написания\nИли напишите название на английском языке')
        bot.delete_message(chat_id=loading.chat.id, message_id=loading.message_id)


@bot.message_handler(state=SearchFilterState.corrections_bd)
def get_corrections(message: Message) -> None:
    """Message handler, that saves city and country name, and sends interactive calendar to choose check-in date"""
    city_name = message.text.split(', ')[0]
    country_code = message.text.split(', ')[2]
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data['country_code'] = country_code
        data['city'] = city_name
    calendar, step = DetailedTelegramCalendar(min_date=datetime.date.today(), locale='ru', calendar_id=3).build()
    bot.send_message(message.chat.id,
                     f'Выберете дату заезда в отель:',
                     reply_markup=calendar)
    bot.set_state(message.from_user.id, SearchFilterState.arrival_date_bd, message.chat.id)


@bot.callback_query_handler(func=DetailedTelegramCalendar.func(calendar_id=3))
def cal(c: CallbackQuery):
    """function that responses to user choice and shows it to make sure no mistakes have been made"""
    result, key, step_i = DetailedTelegramCalendar(min_date=datetime.date.today(), locale='ru', calendar_id=3).process(
        c.data)
    if not result and key:
        bot.edit_message_text(f'Выберете дату заезда в отель:',
                              c.message.chat.id,
                              c.message.message_id,
                              reply_markup=key)
    elif result:
        bot.edit_message_text(f'Вы выбрали: {result}',
                              c.message.chat.id,
                              c.message.message_id)
        keyboard = keyboard_util.create_reply_keyboard([f'{result}'])
        bot.send_message(c.from_user.id, "Выберите:", reply_markup=keyboard)


@bot.message_handler(state=SearchFilterState.arrival_date_bd)
def get_arrival_date(message: Message) -> None:
    """Message handler, that saves check-in date, and sends interactive calendar to choose check-out date"""
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data['arrival_date'] = message.text

    calendar_deport, step_dep = DetailedTelegramCalendar(
        min_date=datetime.date(
            year=int(message.text.split('-')[0]),
            month=int(message.text.split('-')[1]),
            day=int(message.text.split('-')[2])),
        locale='ru',
        calendar_id=4
    ).build()
    bot.send_message(message.chat.id,
                     f'Выберете дату выезда из отеля:',
                     reply_markup=calendar_deport)
    bot.set_state(message.from_user.id, SearchFilterState.deport_date_bd, message.chat.id)


@bot.callback_query_handler(func=DetailedTelegramCalendar.func(calendar_id=4))
def cal(c: CallbackQuery):
    """
    function that responses to user choice and shows it to make sure no mistakes have been made
    (needs to be different than previous one to actually work)
    """
    with bot.retrieve_data(c.from_user.id, c.message.chat.id) as data:
        arrival_date_str = data.get('arrival_date', str(datetime.date.today()))
        try:
            min_date = datetime.date(
                year=int(arrival_date_str.split('-')[0]),
                month=int(arrival_date_str.split('-')[1]),
                day=int(arrival_date_str.split('-')[2]))
        except:
            min_date = datetime.date.today()

    result, key, step_i = DetailedTelegramCalendar(min_date=min_date, locale='ru', calendar_id=4).process(c.data)
    if not result and key:
        bot.edit_message_text(f'Выберете дату выезда из отеля:',
                              c.message.chat.id,
                              c.message.message_id,
                              reply_markup=key)
    elif result:
        bot.edit_message_text(f'Вы выбрали: {result}',
                              c.message.chat.id,
                              c.message.message_id)
        keyboard = keyboard_util.create_reply_keyboard([f'{result}'])
        bot.send_message(c.from_user.id, "Выберите:", reply_markup=keyboard)


@bot.message_handler(state=SearchFilterState.deport_date_bd)
def get_deport_date(message: Message) -> None:
    """saves check-out date and asks for users price range"""
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data['deport_date'] = message.text

    bot.send_message(message.from_user.id, 'Введите диапазон цен через дефис\nПример: 200-400')
    bot.set_state(message.from_user.id, SearchFilterState.price_range_bd, message.chat.id)


@bot.message_handler(state=SearchFilterState.price_range_bd)
def get_price_range(message: Message):
    """saves the price range and proceeds with the result"""
    price_range = message.text.split('-')
    if price_range[0].isdigit() and price_range[1].isdigit():
        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['price_range_min'] = price_range[0]
            data['price_range_max'] = price_range[1]
        bot.set_state(message.from_user.id, SearchFilterState.result_bd, message.chat.id)
        keyboard = keyboard_util.create_reply_keyboard(['Продолжить'])
        bot.send_message(message.from_user.id, "Выберите:", reply_markup=keyboard)
    else:
        bot.send_message(message.from_user.id, 'Введите диапазон цен через дефис\nПример: 200-400')


@bot.message_handler(state=SearchFilterState.result_bd)
def get_result(message: Message) -> None:
    """sends a request to API and saves result in search history db"""
    if message.text.startswith('/'):
        bot.set_state(message.from_user.id, None)
        bot.send_message(message.from_user.id, 'Воспользуйтесь командой ещё раз')
        return
    loading = bot.send_message(message.from_user.id, 'Поиск...')

    try:
        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            dest_response = api_progress.search_destination(data['city'])
            data['dest_id'] = dest_response['data'][0]['dest_id']

            query_dict = {
                "dest_id": data['dest_id'],
                "search_type": "CITY",
                "arrival_date": data["arrival_date"],
                "departure_date": data['deport_date'],
                "price_min": data['price_range_min'],
                "price_max": data['price_range_max'],
                "sort_by": "distance",
                "languagecode": "ru",
                "currency_code": "EUR"
            }

        response = api_progress.search_hotels(query_dict)
        hotels = api_progress.parse_hotels_response(response, data['country_code'])

        if not hotels:
            bot.send_message(message.from_user.id,
                             'Произошла ошибка, либо в городе нет доступных отелей, либо необходимо сменить API')
            bot.delete_message(chat_id=loading.chat.id, message_id=loading.message_id)
            return


        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['hotels'] = hotels
            data['city_name'] = data['city']

            parsed = [data['city'] + " bestdeal"] + hotels

        bot_db.add_search_history(user_id=message.from_user.id, query=parsed)
        parsed.pop(0)
        bot.delete_message(chat_id=loading.chat.id, message_id=loading.message_id)
        send_photo_with_buttons(chat_id=message.from_user.id, index=0)

    except Exception:
        bot.send_message(message.from_user.id,
                         'Произошла ошибка, либо в городе нет доступных отелей, либо необходимо сменить API')
        if len(config.OWNER_ID) > 0:
            bot.send_message(config.OWNER_ID, 'У пользователя возникла ошибка!!!')
        bot.delete_message(chat_id=loading.chat.id, message_id=loading.message_id)


def send_photo_with_buttons(chat_id, index):
    """sends message with suiting hotels, with their description and photo, with option to scroll using buttons"""
    with bot.retrieve_data(chat_id, chat_id) as data:
        hotels = data.get('hotels', [])
        total = len(hotels)
        if total == 0:
            return
        hotel = hotels[index]

    markup = keyboard_util.InlineKeyboardMarkup(row_width=3)
    prev_index = (index - 1) % total
    next_index = (index + 1) % total

    btn_prev = keyboard_util.InlineKeyboardButton("←", callback_data=f"lo {prev_index}")
    btn_current = keyboard_util.InlineKeyboardButton(f"{index + 1}/{total}", callback_data="current")
    btn_next = keyboard_util.InlineKeyboardButton("→", callback_data=f"lo {next_index}")

    markup.add(btn_prev, btn_current, btn_next)

    bot.send_photo(chat_id,
                   photo=hotel['photos'][2],
                   caption=f'Название: {hotel["name"]}\n'
                           f'Ссылка на бронирование: {hotel["booking_link"]}\n'
                           f'(Поправка, некоторые отели могут не открываться по ссылке из-за того что'
                           f' api выдаёт нерабочие, а бот формирует ссылку по названию отеля\n'
                           f'Описание: {hotel["description"]}\nЦена: {hotel["price"]}\n'
                           f'Даты: заезд {hotel["checkin_date"]}, выезд {hotel["checkout_date"]}\n'
                           f'Координаты: {hotel["coordinates"][0]}, {hotel["coordinates"][1]}',
                   reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data.startswith("lo "))
def callback_inline(call: CallbackQuery):
    """function needed for buttons to work"""
    index = int(call.data.split()[1])
    try:
        bot.delete_message(call.message.chat.id, call.message.message_id)
    except:
        pass
    send_photo_with_buttons(call.message.chat.id, index)
    bot.answer_callback_query(call.id)
