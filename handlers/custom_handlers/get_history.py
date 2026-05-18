from loader import bot, config
from telebot.types import Message
import datetime
from utils import keyboard_util, bot_db
from states.history_states import GetHistoryStates
from telegram_bot_calendar import DetailedTelegramCalendar
import ast



def get_search_history(user_id, date_str, query_str=None, limit=10):
    """Function that searches needed record in DB"""
    query = bot_db.SearchHistory.select().where(bot_db.SearchHistory.user_id == user_id)
    target_date = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
    start_of_day = datetime.datetime.combine(target_date, datetime.datetime.min.time())
    end_of_day = datetime.datetime.combine(target_date, datetime.datetime.max.time())

    query = query.where(
        bot_db.SearchHistory.timestamp >= start_of_day,
        bot_db.SearchHistory.timestamp <= end_of_day
    )
    if query_str:
        query = query.where(bot_db.SearchHistory.query.contains(query_str))

    result_query = query.order_by(bot_db.SearchHistory.timestamp.desc()).limit(limit)

    if limit == 1:
        try:
            record = result_query.get()
            parsed = ast.literal_eval(record.query)
            return parsed if isinstance(parsed, list) else [parsed]
        except (bot_db.SearchHistory.DoesNotExist, ValueError, SyntaxError):
            return []
    else:

        records_list = []
        for record in result_query:
            try:
                parsed = ast.literal_eval(record.query)
                records_list.append(parsed if isinstance(parsed, list) else [parsed])
            except (ValueError, SyntaxError):
                continue
        return records_list



@bot.message_handler(commands= ['get_history'])
def get_history(message: Message) -> None:
    """Message handler to a command /get_history, asks for a date of desired search history record"""
    if len(config.OWNER_ID) > 0:
        bot.send_message(config.OWNER_ID,' Кто-то использовал команду: /get_history')
    bot.set_state(message.from_user.id, GetHistoryStates.date, message.chat.id)
    calendar, step = DetailedTelegramCalendar(min_date=datetime.date(day=23, month=12, year=2025), locale='ru', calendar_id=9).build()
    bot.send_message(message.chat.id,
                     f'Выберете дату за которую вы хотите посмотреть историю:',
                     reply_markup=calendar)


@bot.callback_query_handler(func=DetailedTelegramCalendar.func(calendar_id=9))
def cal(c):
    """callback function for calendar"""
    result, key, step_i = DetailedTelegramCalendar(min_date=datetime.date(
        day=23, month=12, year=2025
    ), locale= 'ru', calendar_id=9).process(c.data)
    if not result and key:
        bot.edit_message_text(f'Выберете дату за которую вы хотите посмотреть историю:',
                              c.message.chat.id,
                              c.message.message_id,
                              reply_markup=key)
    elif result:
        bot.edit_message_text(f'Вы выбрали: {result}',
                              c.message.chat.id,
                              c.message.message_id)
        keyboard = keyboard_util.create_reply_keyboard([f'{result}'])
        bot.send_message(c.from_user.id, "Выберите:", reply_markup=keyboard)


@bot.message_handler(state=GetHistoryStates.date)
def choose_history(message: Message) -> None:
    """shows options where user had searched on specific date, and asks to choose city to proceed"""
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data['date'] = message.text
    records = get_search_history(user_id=message.from_user.id, date_str=message.text)

    if not records:
        bot.send_message(message.chat.id, "История за эту дату пуста")
        return

    values_list = records

    buttons = []
    for hotel_list in values_list:
        if hotel_list and len(hotel_list) > 0:
            city = hotel_list[0]
            buttons.append(city)

    keyboard = keyboard_util.create_reply_keyboard(buttons)

    bot.set_state(message.from_user.id, GetHistoryStates.buttons, message.chat.id)
    bot.send_message(message.chat.id, "Выберите город:", reply_markup=keyboard)


@bot.message_handler(state=GetHistoryStates.buttons)
def handle_value_choice(message: Message) -> None:
    """Function sends exact search history record, allowing to scroll through hotels"""
    if message.text.startswith('/'):
        bot.set_state(message.from_user.id, None)
        bot.send_message(message.from_user.id, 'Воспользуйтесь командой ещё раз')
        return
    chosen = message.text.strip()
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        date_str = data['date']
        result = get_search_history(
            user_id=message.from_user.id,
            date_str=date_str,
            query_str=chosen,
            limit=1
        )
        data['result'] = result

    if not result:
        bot.send_message(message.chat.id, f"Не найдена история поиска для '{chosen}'")
        return
    bot.send_message(message.chat.id, f"Вы выбрали: {chosen}")
    send_photo_with_buttons(message.chat.id, index=0)


def send_photo_with_buttons(chat_id, index):
    """Complimentary function for previous one"""
    with bot.retrieve_data(chat_id, chat_id) as data:
        hotels = data['result'][1:]
        total = len(hotels)
        if total == 0:
            return
        hotel = hotels[index]

    markup = keyboard_util.InlineKeyboardMarkup(row_width=3)
    prev_index = (index - 1) % total
    next_index = (index + 1) % total

    btn_prev = keyboard_util.InlineKeyboardButton("←", callback_data=f"vo {prev_index}")
    btn_current = keyboard_util.InlineKeyboardButton(f"{index + 1}/{total}", callback_data="current")
    btn_next = keyboard_util.InlineKeyboardButton("→", callback_data=f"vo {next_index}")

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

@bot.callback_query_handler(func=lambda call: call.data.startswith("vo "))
def callback_inline(call):
    """callback func, allows to scroll"""
    index = int(call.data.split()[1])
    try:
        bot.delete_message(call.message.chat.id, call.message.message_id)
    except:
        pass
    send_photo_with_buttons(call.message.chat.id, index)
    bot.answer_callback_query(call.id)





