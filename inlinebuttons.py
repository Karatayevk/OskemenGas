from aiogram.types import ReplyKeyboardRemove, \
    ReplyKeyboardMarkup, KeyboardButton, \
    InlineKeyboardMarkup, InlineKeyboardButton



# Кнопки главного меню.
what_is_aqi = InlineKeyboardButton('Информация об Air Quality Index ℹ️', callback_data='what_is_aqi')
get_all_info = InlineKeyboardButton('Свод по качеству воздуха в городе 🏙', callback_data='town_info')
get_stantion_info = InlineKeyboardButton('Детальная информация по районам 🏘', callback_data='detail_info')
pollutants_info = InlineKeyboardButton('Уровень загрязнителей в воздухе😷', callback_data='pollutants')
cities_aqi_info = InlineKeyboardButton('Рейтинг городов Казахстана по AQI 📈', callback_data='kz_cities_info')
get_random_fact = InlineKeyboardButton('Случайный факт об экологии 👩🏼‍🏫', callback_data='random_fact')
choice = InlineKeyboardMarkup(row_width=2).add(what_is_aqi).add(get_all_info).add(get_stantion_info).add(pollutants_info).add(cities_aqi_info).add(get_random_fact)

# Возврат к меню или выбор иных действий.
back_to_menu = InlineKeyboardButton('Вернуться к главному меню', callback_data='back')
more_fact = InlineKeyboardButton('Больше случайных фактов об экологии 🌎', callback_data='more_facts')

back_or_random_fact = InlineKeyboardMarkup().add(more_fact).add(back_to_menu)
only_back_menu = InlineKeyboardMarkup().add(back_to_menu)

# Меню при взаимодействии с информацией на станциях качества воздуха.
select_stantion_or_menu = InlineKeyboardMarkup().add(InlineKeyboardButton('Выбрать другой район/улицу 🔄', callback_data='detail_info')).add(back_to_menu)
stantion_info = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton('ЦДК', callback_data='ЦДК'), InlineKeyboardButton('Пристань ', callback_data='Пристань')],
        [InlineKeyboardButton('Бажова', callback_data='Бажова'), InlineKeyboardButton('Ворошилова', callback_data='Ворошилова')],
        [InlineKeyboardButton('КШТ', callback_data='КШТ'), InlineKeyboardButton('Согра', callback_data='Согра')],
        [InlineKeyboardButton('Электротовары', callback_data='Электротовары'), InlineKeyboardButton('Защита', callback_data='Защита')]
    ]
)



