from ast import parse
from itertools import count
import os
os.system('cls' if os.name == 'nt' else 'clear')

import random
import requests
import re
from bs4 import BeautifulSoup
from prettytable import PrettyTable,ALL
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
from prettytable import SINGLE_BORDER
import aioschedule
from datetime import datetime
import pytz
import asyncio
import aqi_description_funcs, inlinebuttons, facts_list, random_headers
from aiogram.utils.exceptions import (MessageToEditNotFound, MessageCantBeEdited, MessageCantBeDeleted, MessageToDeleteNotFound)


bot = Bot(token='your_tgbot_token')
dp = Dispatcher(bot)


# Словарь для сбора статистики взаимодействий с ботом (числа увеличиваются при отправке команд пользователями).
# Данные обнуляются при рестарте на стороне хостинга, гораздо правильней для сбора данных использовать записи в БД.
actions_counter = {
    'what is aqi' : 0,
    'bot start' : 0,
    'town info' : 0,
    'stantion info' : 0,
    'pollutants info' : 0,
    'ranking KZ cities' : 0,
    'random facts' : 0,
    'unknown commands' : 0
}

async def counter_increase(choice):
    global actions_counter
    actions_counter[choice] += 1


headers = {
    'User-Agent' : 'your_useragent_info'
}

r = requests.get('https://www.iqair.com/ru/kazakhstan/east-kazakhstan/ust-kamenogorsk', headers=headers)
soup = BeautifulSoup(r.text, 'lxml')

# Отправка запроса к странице сайта, страница содержит информацию о качестве воздуха в городе и его районах.
async def send_request():
    current_data = datetime.now(pytz.timezone("Asia/Almaty"))
    current_hour = current_data.strftime("%H")
    if int(current_hour) >= 6:
        print(f'[INFO]: Направляем запрос к cайту: {current_data.strftime("%H:%M:%S")}')
        global r, headers, soup
        headers = {
            'User-Agent' : random_headers.rnd_headers[random.randint(0,500)]
        }

        r = requests.get('https://www.iqair.com/ru/kazakhstan/east-kazakhstan/ust-kamenogorsk', headers=headers)
        if r.status_code == 200:
            soup = BeautifulSoup(r.text, 'lxml')
            print(f'[INFO]: Запрос выполнен успешно: {current_data.strftime("%H:%M:%S")} , {headers["User-Agent"]}')
        else:
            print(f'[INFO]: Запрос не вернул успешный статус, обновление не проведено.')
            pass
    else:
        print(f'[INFO]: Вне времени обновления, обновление приостановлено: {current_data.strftime("%H:%M:%S")}')

# Функция возвращает словарь с информацией о качестве воздуха из спарсенных и обработанных данных.
def dct_info():
    
    data = soup.find(class_ = 'ranking__table', title="Рейтинг Усть-Каменогорск по качеству воздуха в реальном времени")

    rep = {
            '#stationAQI США1 ': '',
            'Ust-Kamanogorsk - no.2: Piterskikh Kommunarov' : 'Пристань ',
            'Ust-Kamanogorsk - no.3: Voroshilov st.' : 'Ворошилова ',
            'Rabochaya street 6' : 'Бажова ',
            'Satpayev st. 12' : 'КШТ ',
            'Tynyshpayev st. 126' : 'Защита ',
            'Electrical Goods' : 'Электротовары ',
            'CDC' : 'ЦДК ',
            'Egorova st. 6' : 'Согра '
        }


    rep = dict((re.escape(k), v) for k,v in rep.items())
    pattern = re.compile('|'.join(rep.keys()))
    stantion_data = pattern.sub(lambda m: rep[re.escape(m.group(0))], data.text).split()

    del stantion_data[2::3]

    stantion_data = list(map(lambda el:[int(el), aqi_description_funcs.aqi_shortdescription(int(el))] if stantion_data.index(el) % 2 != 0 else el, stantion_data))
    dct = dict(zip(stantion_data[::2], stantion_data[1::2]))
    return dct

# Создание таблицы c информацией по станциям качества воздуха.
def stantion_info_table():
    table = PrettyTable(border=False,preserve_internal_border=False)
    table.set_style(SINGLE_BORDER)
    table.hrules=ALL
    table.field_names = ['Расположение', 'AQI','Качество']
    table.add_rows(
        [
        ['станции',' 💨 ','воздуха'],
        ['','','']
        ])

    for k,v in dct_info().items():
        table.add_row([str.ljust(k,13),str.ljust(str(v[0]),3), str.ljust(v[1],10)])
    return table

# Функция возвращает таблицу с информацией о концентрации загрязнителей воздуха.
def pollutants_table_info():
    pollutants = soup.find('table', class_ ='aqi-overview-detail__other-pollution-table').text.split(' ')
    del pollutants[0]
    pollutants = [(re.sub(r'µg/m³', '', x)) for x in pollutants]
    pollutants = [float(str(x.replace('*',''))) if y % 2 != 0 else str(x.replace('*','')) for y,x in enumerate(pollutants)]
    pollutants_dct = {}

    for i in range(0,len(pollutants),2):
        if i == len(pollutants)-1:
            break
        else:
            pollutants_dct[pollutants[i]] = pollutants[i+1]


    recommended_values24h = {'PM2.5': 15.0, 'PM10' : 45.0, 'SO2' : 40.0, 'CO':'-', 'NO2' : '-'}

    pollutants_table = PrettyTable(border=False,preserve_internal_border=False)

    pollutants_table.set_style(SINGLE_BORDER)
    pollutants_table.hrules=ALL
    pollutants_table.field_names = ['Загрязнитель', 'Концентрация', 'Норма']


    pollutants_table.add_rows(
        [
            ['', 'µg/m³', 'µg/m³'],
            ['','','']
        ]
    )

    for k,v in pollutants_dct.items():
        pollutants_table.add_row([str.ljust(k,5), f'{str.rjust(str(v),5)}' if k == 'CO' or k == 'NO2' else f'{str.rjust(str(v),5)}🟢' if v <= recommended_values24h[k] else f'{str.rjust(str(v),5)}🔴', recommended_values24h[k]])
    
    return pollutants_table

# Функция возвращает таблицу с рейтингом городов Казахстана по уровню AQI (Air Quality Index).
def cities_ranking_table():            
    cities_info = str(soup.find("table", class_ = "ranking__table"))
    cities_list = [word[1].replace(',','') for word in map(str.split, re.findall(r'href="[^\s]* [^\s]*',cities_info))]
    aqi_in_cities = [int(word[1]) for word in map(str.split, re.findall(r'-pill"> [^\s]*',cities_info))]
    nums = list(range(1,11))
    aqi_in_cities = [str(i) + '🟢' if i <= 50 else str(i) + '🟡' if 51 <= i <= 100 else str(i) + '🟠' if 101 <= i <= 150 else str(i) + '🔴' for i in aqi_in_cities]
    aqi_cities_table = PrettyTable(border=False,preserve_internal_border=False)
    aqi_cities_table.field_names = ["#", 'Город', 'AQI USA']
    for i in range(len(cities_list)):
        aqi_cities_table.add_row([nums[i], str.ljust(cities_list[i],18), str.rjust(aqi_in_cities[i],4)])
    return aqi_cities_table

# Функция возвращает время обновления данных на странице сайта , к которому бот обращается.
def get_date():  
    date_info = soup.find(class_ = 'timestamp__wrapper').text
    return date_info

# Создание хендлеров и асинхронных функций , для получения запроса от пользователей и отправки необходимой информации.
@dp.message_handler(commands=['secret_stats'])
async def command_start(message : types.Message):
    stats_table = PrettyTable(border=False,preserve_internal_border=False)
    stats_table.field_names = ["action".center(17) , "count".center(6)]
    for k,v in actions_counter.items():
        stats_table.add_row([str.ljust(k,25), str.rjust(str(v),6)])
    await bot.send_message(message.from_user.id, f'Note: when the server is restarted, the data is reset.')
    await bot.send_message(message.from_user.id, f'actions with bot:\n<pre>{stats_table}</pre>', parse_mode='html')

@dp.message_handler(commands=['help'])
async def command_start(message : types.Message):
    await message.answer(
f'Для взаимодействия с ботом , используйте команду /gas.')

@dp.message_handler(commands=['start'])
async def gas_info(message: types.Message):
    await counter_increase('bot start')
    await bot.send_message(chat_id='843683451', text = f"""[INFO]: Пользователь: {message.from_user.username} запустил бота. 
[INFO]: Имя - {message.from_user.first_name}.
[INFO]: Фамилия - {message.from_user.last_name}.""")
    await bot.send_message(message.from_user.id, f'Привет! Данный бот собирает информацию о качестве воздуха в г.Усть-Каменогорск \
и предоставляет ее пользователям по запросу. Взаимодействие с ботом осуществляется выбором соответствующих кнопок в меню. \n\n\
В случае , если потребуется повторный вывод меню , используйте команду /gas.')
    await bot.send_message(message.from_user.id,'Выберите действие', reply_markup=inlinebuttons.choice)


@dp.message_handler(commands=['gas'])
async def gas_info(message: types.Message):
    await counter_increase('bot start')
    await bot.send_message(chat_id='843683451', text = f"""[INFO]: Пользователь: {message.from_user.username} начал взаимодействие с ботом. 
[INFO]: Имя - {message.from_user.first_name}.
[INFO]: Фамилия - {message.from_user.last_name}.""")
    await bot.send_message(message.from_user.id, 'Выберите действие:', reply_markup=inlinebuttons.choice)

@dp.callback_query_handler(text='town_info')
async def send_town_info(message: types.Message):
        await counter_increase('town info')
        await bot.send_message(chat_id='843683451', text = f'[INFO]: Пользователь: {message.from_user.username} ({message.from_user.first_name} {message.from_user.last_name}) запросил свод по городу.')
        try:
            await bot.delete_message(message.from_user.id, message.message.message_id)
        except MessageCantBeDeleted:
            await bot.send_message(chat_id='843683451', text = f'[INFO]: Пользователь: {message.from_user.username} error message cant be deleteted')
            await bot.send_message(message.from_user.id, f'Air Quality Index (AQI) - индекс качества воздуха, чем выше показатель - тем более загрязнен воздух.')
            await bot.send_message(message.from_user.id, f'<pre>{stantion_info_table()}</pre>', parse_mode='html')
            await bot.send_message(message.from_user.id, f'{get_date()}')
        except MessageToDeleteNotFound:
            await bot.send_message(chat_id='843683451', text = f'[INFO]: Пользователь: {message.from_user.username} error message to dele not found')
            await bot.send_message(message.from_user.id, f'Air Quality Index (AQI) - индекс качества воздуха, чем выше показатель - тем более загрязнен воздух.')
            await bot.send_message(message.from_user.id, f'<pre>{stantion_info_table()}</pre>', parse_mode='html')
            await bot.send_message(message.from_user.id, f'{get_date()}')
        else:
            await bot.send_message(message.from_user.id, f'Air Quality Index (AQI) - индекс качества воздуха, чем выше показатель - тем более загрязнен воздух.')
            await bot.send_message(message.from_user.id, f'<pre>{stantion_info_table()}</pre>', parse_mode='html')
            await bot.send_message(message.from_user.id, f'{get_date()}')
        await bot.send_message(message.from_user.id, 'Выберите действие:', reply_markup=inlinebuttons.only_back_menu)


@dp.callback_query_handler(text='detail_info')
async def send_town_info(message: types.Message):
        await bot.send_message(message.from_user.id, 'Выберите станцию для получения детальной информации:', reply_markup=inlinebuttons.stantion_info)



@dp.callback_query_handler(text='what_is_aqi')
async def send_town_info(message: types.Message):
        await counter_increase('what is aqi')
        try:
            await bot.delete_message(message.from_user.id, message.message.message_id)
        except MessageCantBeDeleted:
            await bot.send_message(chat_id='843683451', text = f'[INFO]: Пользователь: {message.from_user.username} error message delete')
        await bot.send_photo(message.from_user.id, photo='https://i.imgur.com/RqkESG1.jpg')
        await bot.send_photo(message.from_user.id, photo='https://i.imgur.com/UvzOwGs.jpg')
        await bot.send_message(message.from_user.id, 'Источник информации - iqair.com.')
        await bot.send_message(message.from_user.id, 'Выберите действие:', reply_markup=inlinebuttons.choice)


@dp.callback_query_handler(text='random_fact')
async def send_town_info(message: types.Message):
        await counter_increase('random facts')
        try:
            await bot.delete_message(message.from_user.id, message.message.message_id)
        except MessageCantBeDeleted:
            await bot.send_message(chat_id='843683451', text = f'[INFO]: Пользователь: {message.from_user.username} error message delete')
        await bot.send_message(message.from_user.id, f"""Случайный факт📚:
        
{facts_list.facts[random.randint(0,52)]}""")
        await bot.send_message(message.from_user.id, 'Выберите действие:', reply_markup=inlinebuttons.back_or_random_fact)

@dp.callback_query_handler(text='more_facts')
async def send_more_facts(message: types.Message):
    await counter_increase('random facts')
    try:
        await bot.delete_message(message.from_user.id, message.message.message_id)
    except MessageCantBeDeleted:
        await bot.send_message(chat_id='843683451', text = f'[INFO]: Пользователь: {message.from_user.username} error message delete')
    await bot.send_message(message.from_user.id, f'Еще случайный факт📚:\n\n{facts_list.facts[random.randint(0,52)]}')
    await bot.send_message(message.from_user.id, 'Выберите действие:', reply_markup=inlinebuttons.back_or_random_fact)

@dp.callback_query_handler(text='back')
async def send_more_facts(message: types.Message):
    try:
        await bot.delete_message(message.from_user.id, message.message.message_id)
    except MessageCantBeDeleted:
        await bot.send_message(chat_id='843683451', text = f'[INFO]: Пользователь: {message.from_user.username} error message delete')
    await bot.send_message(message.from_user.id, 'Выберите действие:', reply_markup=inlinebuttons.choice)



@dp.callback_query_handler(lambda c: c.data and c.data in ['Пристань','Согра','Защита','Бажова','КШТ','Электротовары','ЦДК','Ворошилова'])
async def process_callback_button1(callback_query: types.CallbackQuery):
        await counter_increase('stantion info')
        await bot.send_message(chat_id='843683451', text = f'[INFO]: Пользователь: {callback_query.from_user.username} ({callback_query.from_user.first_name} {callback_query.from_user.last_name}) запросил свод по району {callback_query.data}')
        await bot.answer_callback_query(callback_query.id)  
        try:
            await bot.delete_message(callback_query.from_user.id, callback_query.message.message_id)
        except MessageCantBeDeleted:
            await bot.send_message(chat_id='843683451', text = f'[INFO]: Пользователь: {callback_query.from_user.username} error message delete')         
        try:
            await bot.send_message(callback_query.from_user.id, f'Станция: {callback_query.data}\n\n{aqi_description_funcs.aqi_longdescription(dct_info()[callback_query.data][0])}\n\n{get_date()}')
        except KeyError:
            await bot.send_message(callback_query.from_user.id, f"""
Данные на платформе iqair по станции '{callback_query.data}' временно недоступны.

Вы можете просмотреть данные по другим районам или вернуться к меню.
""")
        await bot.send_message(callback_query.from_user.id, 'Выберите действие', reply_markup=inlinebuttons.select_stantion_or_menu)

@dp.callback_query_handler(text='pollutants')
async def send_pollutants_info(message: types.Message):
        await counter_increase('pollutants info')
        await bot.send_message(chat_id='843683451', text = f'[INFO]: Пользователь: {message.from_user.username} ({message.from_user.first_name} {message.from_user.last_name}) запросил свод по загрязнителям.')
        try:
            await bot.delete_message(message.from_user.id, message.message.message_id)
        except MessageCantBeDeleted:
            await bot.send_message(chat_id='843683451', text = f'[INFO]: Пользователь: {message.from_user.username} error message delete')
        await bot.send_photo(message.from_user.id, photo='https://imgur.com/a/b99Bn13')
        await bot.send_message(message.from_user.id, f'<pre>{pollutants_table_info()}</pre>', parse_mode='html')  
        await bot.send_message(message.from_user.id, f"""{get_date()}

📌Примечания:
🟢 - показатель меньше или равен среднесуточной норме. 
🔴 - показатель выше среднесуточной нормы.  
µg/m³ = мкг/м³
Среднесуточные нормы указаны в соответствии с рекомендациями Всемирной организации здравоохранения.""")
        await bot.send_message(message.from_user.id, 'Выберите действие:', reply_markup=inlinebuttons.only_back_menu)

@dp.callback_query_handler(text='kz_cities_info')
async def send_ranking_info(message: types.Message):
        await counter_increase('ranking KZ cities')
        await bot.send_message(chat_id='843683451', text = f'[INFO]: Пользователь: {message.from_user.username} ({message.from_user.first_name} {message.from_user.last_name}) запросил свод по городам Казахстана.')
        try:
            await bot.delete_message(message.from_user.id, message.message.message_id)
        except MessageCantBeDeleted:
            await bot.send_message(chat_id='843683451', text = f'[INFO]: Пользователь: {message.from_user.username} error message delete')
        await bot.send_message(message.from_user.id, f'📌Примечание: чем выше уровень AQI - тем более загрязнен воздух.\n\n{get_date()}')
        await bot.send_message(message.from_user.id, f'<pre>{cities_ranking_table()}</pre>', parse_mode='html')  
        await bot.send_message(message.from_user.id, 'Выберите действие:', reply_markup=inlinebuttons.only_back_menu)

@dp.message_handler()
async def unknown_command(message: types.Message):
        await counter_increase('unknown commands')
        await bot.send_message(chat_id='843683451', text = f'[INFO]: Пользователь: {message.from_user.username} ({message.from_user.first_name} {message.from_user.last_name}) ввел неизвестную команду - {message.text}.')
        await message.reply(f'Вы ввели неизвестную команду , для взаимодействия с ботом, используйте команду: /gas.')

# Установка расписания на отправку запросов к странице сайта iqair.com.
async def scheduler():
    aioschedule.every().hour.at(":35").do(send_request)
    while True:
        await aioschedule.run_pending() 
        await asyncio.sleep(1)

# Создание задачи по запуску функции.
async def on_startup(_):
    asyncio.create_task(scheduler())


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)
