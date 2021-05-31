# get запрос IPA к open weather и news, чтоб получить данные погоды
import requests

# преобразовываем Восход и Закат в читаемый формат
import datetime

# импортируем токены в этот файл
from config import tg_bot_token, open_weather_token

# из библеотки aiogram импортируем Бота, Типы, Диспетчер, Экзекъютер
from aiogram import Bot, types, Dispatcher, executor

# для извлечения данных из файлов HTML
from bs4 import BeautifulSoup

# создаем объект бота, передаем в него наш токен
bot = Bot(token=tg_bot_token)

# создаем диспетчер, чтоб управлять handler и передаем в него нашего бота
dp = Dispatcher(bot)


# СТАРТ/ПРИВЕТСТВИЕ
@dp.message_handler(commands=['start'])
# функция для ответа на команду /start
async def start(message: types.Message):
    await message.reply(f"<b>Здравствуй, {message.from_user.first_name}!</b>\nЧто тебя интересует?\n***\n"
                        f"Бот может выполнять команды:\n"
                        f"<b>/news</b> - новости\n"
                        f"<b>/weather</b> - погода", parse_mode='html')


# НОВОСТИ
@dp.message_handler(commands=['news'])
# функция парсинга и вывода
async def news(message):
    # ссылка сайта c которого парсим нужные нам данные
    URL = 'https://ria.ru/world/'

    # в браузере вводим get my user agent => User-Agent
    # переменная HEADERS - это список, где находится User-Agent, он нам нужен для дальнейшей работы
    HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36'}

    # далее получаем свою страницу response c методом requests.get
    response = requests.get(URL, headers=HEADERS)

    # отправляем сюда контент страницы, которую мы скачали
    soup = BeautifulSoup(response.content, 'html.parser')

    # вписываем сюда необходимы тег и класс(ищем их на страничке через F12)
    texts = soup.findAll('a', 'list-item__title')

    # выбираем через цикл сколько хотим новостей увидеть в чате бота
    for i in range(len(texts[:-16]), -1, -1):
        txt = str(i + 1) + ') ' + texts[i].text
        await message.reply('<a href="{}">{}</a>'.format(texts[i]['href'], txt), parse_mode='html')


# ПОГОДА
@dp.message_handler(commands=["weather"])
# функция для ответа на команду /weather
async def weather_command(message: types.Message):
    await message.reply("Напиши мне название города и ты получишь ответ")


@dp.message_handler()
# создадим функцию с помощью которой получаем погоду
async def get_weather(message: types.Message):
    # создаем словарь из картинок для погоды
    code_to_smile = {
        "Clear": "Ясно \U00002600",
        "Clouds": "Облачно \U00002601",
        "Rain": "Дождь \U00002614",
        "Drizzle": "Дождь \U00002614",
        "Thunderstorm": "Гроза \U000026A1",
        "Snow": "Снег \U0001F328",
        "Mist": "Туман \U0001F328"
    }

    # делаем проверку
    try:
        # формируем запрос / units=metric - меняем температуру с к            на градусы цельсия
        r = requests.get(
            f"http://api.openweathermap.org/data/2.5/weather?q={message.text}&appid={open_weather_token}&units=metric")

        # парсим json погоды
        data = r.json()
        # обращаемся к ключам чтоб выводить значения

        # название
        city = data["name"]
        # температура
        cur_weather = data["main"]["temp"]
        # описание погоды
        weather_description = data["weather"][0]["main"]
        # условие, если совпадет значение с нашим словарем картинок, то мы одну из них выведем
        if weather_description in code_to_smile:
            wd = code_to_smile[weather_description]
        # если нет, то выведим сообщение
        else:
            wd = "Невозможно определить погоду!"

        # влажность
        humidity = data["main"]["humidity"]
        # давление
        pressure = data["main"]["pressure"]
        # ветер
        wind = data["wind"]["speed"]

        # преобразуем sunrise и sunset в читаемый формат используя модуль datetime
        # отметка времени восхода солнца
        sunrise_timestamp = datetime.datetime.fromtimestamp(data["sys"]["sunrise"])
        # метка времени заката
        sunset_timestamp = datetime.datetime.fromtimestamp(data["sys"]["sunset"])
        # продолжительность дня
        length_of_the_day = datetime.datetime.fromtimestamp(data["sys"]["sunset"]) - datetime.datetime.fromtimestamp(
            data["sys"]["sunrise"])
        # выводим сообщение пользователю
        await message.reply(f"***{datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}***\n"
              f"Погода в городе: {city}\nТемпература: {cur_weather}C° {wd}\n"
              f"Влажность: {humidity}%\nДавление: {pressure} мм.рт.ст.\nВетер: {wind} м/с\n"
              f"Восход солнца: {sunrise_timestamp}\n"
              f"Закат солнца: {sunset_timestamp}\n"
              f"Продолжительность дня: {length_of_the_day}\n"
              f"***Хорошего дня!***")
    except:
        # если пользователь введет не правильную команду или же город, то сообщаем об ошибке
        await message.reply("Ошибка, проверьте правильность сообщения! \U00002620")


# запускаем бота
if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
