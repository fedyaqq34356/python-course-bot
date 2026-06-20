from config import PYTHON_TOPICS, AIOGRAM_TOPICS
from utils import format_progress_bar
from database import Database

class CourseManager:
    """Менеджер для управления прогрессом курсов."""
    
    def __init__(self):
        # Инициализируем базу данных
        self.db = Database()
    
    def get_topics(self, course_type: str) -> list:
        """Получает список тем для курса."""
        if course_type == "python":
            return PYTHON_TOPICS
        elif course_type == "aiogram":
            return AIOGRAM_TOPICS
        return []
    
    def get_user_progress(self, user_id: int, course_type: str) -> int:
        """Получает прогресс пользователя для конкретного курса."""
        return self.db.get_user_progress(user_id, course_type)
    
    def update_user_progress(self, user_id: int, course_type: str, topic_num: int):
        """Обновляет прогресс пользователя."""
        self.db.update_user_progress(user_id, course_type, topic_num)
        self.db.update_user_activity(user_id)
    
    def register_user(self, user_id: int, username: str = None, first_name: str = None, last_name: str = None):
        """Регистрирует пользователя в системе."""
        self.db.add_user(user_id, username, first_name, last_name)
    
    def save_solution(self, user_id: int, course_type: str, topic_num: int, task: str, solution: str, feedback: str):
        """Сохраняет решение пользователя."""
        self.db.save_user_solution(user_id, course_type, topic_num, task, solution, feedback)
    
    def format_topics_list(self, user_id: int, course_type: str) -> str:
        """Форматирует список тем с прогрессом."""
        topics = self.get_topics(course_type)
        progress = self.get_user_progress(user_id, course_type)
        
        course_name = "PYTHON" if course_type == "python" else "AIOGRAM"
        course_emoji = "🐍" if course_type == "python" else "🤖"
        
        text = f"{course_emoji} <b>КУРС {course_name}</b>\n"
        text += f"📊 Прогресс: {format_progress_bar(progress, len(topics))}\n"
        text += f"✅ Пройдено: {progress}/{len(topics)} тем\n\n"
        
        for i, topic in enumerate(topics, 1):
            if i <= progress:
                status = "✅"
            elif i == progress + 1:
                status = "🔄"
            else:
                status = "⏳"
            
            text += f"{status} <b>{i}.</b> {topic}\n"
        
        return text
    
    def format_full_progress(self, user_id: int) -> str:
        """Форматирует полный прогресс пользователя по всем курсам."""
        python_progress = self.get_user_progress(user_id, "python")
        aiogram_progress = self.get_user_progress(user_id, "aiogram")
        
        python_total = len(PYTHON_TOPICS)
        aiogram_total = len(AIOGRAM_TOPICS)
        
        # Получаем статистику пользователя
        stats = self.db.get_user_stats(user_id)
        
        text = "📊 <b>ВАШ ОБЩИЙ ПРОГРЕСС</b>\n\n"
        
        text += f"🐍 <b>Python курс:</b>\n"
        text += f"   {format_progress_bar(python_progress, python_total)}\n"
        text += f"   Пройдено: {python_progress}/{python_total} тем\n\n"
        
        text += f"🤖 <b>Aiogram курс:</b>\n"
        text += f"   {format_progress_bar(aiogram_progress, aiogram_total)}\n"
        text += f"   Пройдено: {aiogram_progress}/{aiogram_total} тем\n\n"
        
        total_progress = python_progress + aiogram_progress
        total_topics = python_total + aiogram_total
        
        text += f"🎯 <b>Общий прогресс:</b>\n"
        text += f"   {format_progress_bar(total_progress, total_topics)}\n"
        text += f"   Завершено: {int((total_progress/total_topics)*100) if total_topics > 0 else 0}% обучения\n\n"
        
        text += f"📝 <b>Статистика:</b>\n"
        text += f"   Решений отправлено: {stats['solutions_count']}\n"
        
        if stats['created_at']:
            text += f"   Начали обучение: {stats['created_at'][:10]}\n\n"
        
        if total_progress == 0:
            text += "🚀 Начните с курса Python, чтобы освоить основы!"
        elif python_progress == python_total and aiogram_progress == 0:
            text += "🎉 Python освоен! Переходите к изучению Aiogram!"
        elif total_progress == total_topics:
            text += "🏆 Поздравляем! Вы завершили все курсы!"
        else:
            if python_progress < python_total:
                next_topic = PYTHON_TOPICS[python_progress]
                text += f"📚 Следующая тема Python: <i>{next_topic}</i>\n"
            if aiogram_progress < aiogram_total and python_progress == python_total:
                next_topic = AIOGRAM_TOPICS[aiogram_progress]
                text += f"📚 Следующая тема Aiogram: <i>{next_topic}</i>\n"
        
        return text
    
    def can_access_aiogram(self, user_id: int) -> bool:
        """Проверяет, может ли пользователь получить доступ к курсу Aiogram."""
        python_progress = self.get_user_progress(user_id, "python")
        return python_progress >= len(PYTHON_TOPICS)  # Должен завершить Python курс
    
    def get_system_stats(self) -> str:
        """Получает статистику всей системы."""
        total_users = self.db.get_all_users_count()
        return f"👥 Всего пользователей в боте: {total_users}"