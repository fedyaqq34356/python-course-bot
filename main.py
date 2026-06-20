import asyncio
import logging
from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart, Command
from aiogram.fsm.storage.memory import MemoryStorage

from config import BOT_TOKEN
from states import StudyStates
from handlers import (
    start_handler, course_selection_handler, show_progress, show_help,
    course_callback_handler, study_topic_callback, get_task_callback,
    check_solution_handler, collect_solution, agreement_callback_handler
)

# Настройка логирования
logging.basicConfig(level=logging.INFO)

class PythonCourseBot:
    def __init__(self):
        self.bot = Bot(token=BOT_TOKEN)
        self.dp = Dispatcher(storage=MemoryStorage())
        
        # Регистрация хендлеров
        self.register_handlers()
    
    def register_handlers(self):
        """Регистрирует хендлеры бота."""
        
        # Команды
        self.dp.message.register(start_handler, CommandStart())
        self.dp.message.register(check_solution_handler, StudyStates.waiting_for_solution, Command("ready"))
        
        # Кнопки главного меню
        self.dp.message.register(course_selection_handler, F.text == "📚 Выбрать курс")
        self.dp.message.register(show_progress, F.text == "📊 Мой прогресс")
        self.dp.message.register(show_help, F.text == "ℹ️ Помощь")
        
        # Callback кнопки
        self.dp.callback_query.register(course_callback_handler, F.data.startswith("course_"))
        self.dp.callback_query.register(study_topic_callback, F.data.startswith("study_"))
        self.dp.callback_query.register(get_task_callback, F.data.startswith("task_"))
        
        # Callback для соглашения
        self.dp.callback_query.register(
            agreement_callback_handler,
            F.data.in_(["accept_agreement", "decline_agreement"])
        )
        
        # Сбор решения
        self.dp.message.register(collect_solution, StudyStates.waiting_for_solution, F.text)
    
    async def start(self):
        """Запускает бота."""
        print("🤖 Python Course Bot запущен!")
        await self.dp.start_polling(self.bot)


# Запуск бота
async def main():
    bot = PythonCourseBot()
    try:
        await bot.start()
    except KeyboardInterrupt:
        print("👋 Бот остановлен!")

if __name__ == "__main__":
    asyncio.run(main())