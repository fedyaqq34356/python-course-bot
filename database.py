import sqlite3
import logging
from datetime import datetime
import os

class Database:
    """Класс для работы с базой данных пользователей."""
    
    def __init__(self, db_path: str = "users.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Инициализация базы данных."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Таблица пользователей
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS users (
                        user_id INTEGER PRIMARY KEY,
                        username TEXT,
                        first_name TEXT,
                        last_name TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # Таблица прогресса по курсам
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS user_progress (
                        user_id INTEGER,
                        course_type TEXT,
                        topic_number INTEGER DEFAULT 0,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        PRIMARY KEY (user_id, course_type),
                        FOREIGN KEY (user_id) REFERENCES users (user_id)
                    )
                ''')
                
                # Таблица решений пользователей
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS user_solutions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER,
                        course_type TEXT,
                        topic_number INTEGER,
                        task TEXT,
                        solution TEXT,
                        feedback TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (user_id) REFERENCES users (user_id)
                    )
                ''')
                
                conn.commit()
                logging.info("Database initialized successfully")
                
        except sqlite3.Error as e:
            logging.error(f"Database initialization error: {e}")
    
    def add_user(self, user_id: int, username: str = None, first_name: str = None, last_name: str = None):
        """Добавляет нового пользователя или обновляет существующего."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT OR REPLACE INTO users 
                    (user_id, username, first_name, last_name, last_activity)
                    VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
                ''', (user_id, username, first_name, last_name))
                
                conn.commit()
                
        except sqlite3.Error as e:
            logging.error(f"Error adding user {user_id}: {e}")
    
    def get_user_progress(self, user_id: int, course_type: str) -> int:
        """Получает прогресс пользователя по курсу."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT topic_number FROM user_progress 
                    WHERE user_id = ? AND course_type = ?
                ''', (user_id, course_type))
                
                result = cursor.fetchone()
                return result[0] if result else 0
                
        except sqlite3.Error as e:
            logging.error(f"Error getting progress for user {user_id}: {e}")
            return 0
    
    def update_user_progress(self, user_id: int, course_type: str, topic_number: int):
        """Обновляет прогресс пользователя."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Получаем текущий прогресс
                current_progress = self.get_user_progress(user_id, course_type)
                
                # Обновляем только если новый прогресс больше текущего
                if topic_number > current_progress:
                    cursor.execute('''
                        INSERT OR REPLACE INTO user_progress 
                        (user_id, course_type, topic_number, updated_at)
                        VALUES (?, ?, ?, CURRENT_TIMESTAMP)
                    ''', (user_id, course_type, topic_number))
                    
                    conn.commit()
                    
        except sqlite3.Error as e:
            logging.error(f"Error updating progress for user {user_id}: {e}")
    
    def save_user_solution(self, user_id: int, course_type: str, topic_number: int, 
                          task: str, solution: str, feedback: str):
        """Сохраняет решение пользователя."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT INTO user_solutions 
                    (user_id, course_type, topic_number, task, solution, feedback)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (user_id, course_type, topic_number, task, solution, feedback))
                
                conn.commit()
                
        except sqlite3.Error as e:
            logging.error(f"Error saving solution for user {user_id}: {e}")
    
    def get_user_stats(self, user_id: int) -> dict:
        """Получает статистику пользователя."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Прогресс по курсам
                cursor.execute('''
                    SELECT course_type, topic_number FROM user_progress 
                    WHERE user_id = ?
                ''', (user_id,))
                
                progress = {row[0]: row[1] for row in cursor.fetchall()}
                
                # Количество решений
                cursor.execute('''
                    SELECT COUNT(*) FROM user_solutions WHERE user_id = ?
                ''', (user_id,))
                
                solutions_count = cursor.fetchone()[0]
                
                # Дата регистрации
                cursor.execute('''
                    SELECT created_at FROM users WHERE user_id = ?
                ''', (user_id,))
                
                created_at = cursor.fetchone()
                created_at = created_at[0] if created_at else None
                
                return {
                    'progress': progress,
                    'solutions_count': solutions_count,
                    'created_at': created_at
                }
                
        except sqlite3.Error as e:
            logging.error(f"Error getting stats for user {user_id}: {e}")
            return {'progress': {}, 'solutions_count': 0, 'created_at': None}
    
    def get_all_users_count(self) -> int:
        """Получает общее количество пользователей."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('SELECT COUNT(*) FROM users')
                return cursor.fetchone()[0]
                
        except sqlite3.Error as e:
            logging.error(f"Error getting users count: {e}")
            return 0
    
    def update_user_activity(self, user_id: int):
        """Обновляет время последней активности пользователя."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    UPDATE users SET last_activity = CURRENT_TIMESTAMP 
                    WHERE user_id = ?
                ''', (user_id,))
                
                conn.commit()
                
        except sqlite3.Error as e:
            logging.error(f"Error updating activity for user {user_id}: {e}")