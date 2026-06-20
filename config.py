import os
from dotenv import load_dotenv

load_dotenv()

# Конфигурация бота
BOT_TOKEN = os.getenv("BOT_TOKEN")

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN не найден в переменных окружения")

# Настройки курсов
PYTHON_TOPICS = [
    "Что такое программирование и Python",
    "Первые шаги — вывод текста", 
    "Переменные — хранение данных",
    "Типы данных",
    "Операции с числами",
    "Работа со строками",
    "Ввод данных от пользователя",
    "Условия — принятие решений",
    "Циклы — повторение действий",
    "Списки — хранение нескольких элементов",
    "Функции — группировка кода",
    "Словари — данные с ключами",
    "Обработка ошибок",
    "Работа с файлами"
]

AIOGRAM_TOPICS = [
    "Создание Telegram ботов на AIOGRAM 3.4",
    "Фильтры и работа с сообщениями на AIOGRAM 3.4",
    "Роутеры и структура Telegram бота на AIOGRAM 3.4",
    "Клавиатура в Telegram ботах — Inline, Reply и Builder на AIOGRAM 3.4",
    "CallbackQuery на AIOGRAM 3.4",
    "FSM Context — машина состояний на AIOGRAM 3.4",
    "Middleware на AIOGRAM 3.4",
    "Телеграм бот на Python с нуля — Aiogram для начинающих",
    "База данных и выгрузка на сервер Telegram бота на Python — Aiogram 3",
    "Деплой бота на сервер | AIOGRAM 3"
]

# Настройки сообщений
MAX_MESSAGE_LENGTH = 1000