import g4f
import re
import logging

class GPTService:
    """Сервис для работы с GPT через g4f."""
    
    # Строгое соответствие номера урока изученным концепциям
    TOPIC_CONCEPTS = {
        1: ["print()", "строки в кавычках", "вывод текста"],
        2: ["print()", "переменные", "присваивание ="],
        3: ["переменные", "int", "str", "float", "type()"],
        4: ["числа", "+", "-", "*", "/", "математические операции"],
        5: ["строки", "конкатенация +", "кавычки", "len()"],
        6: ["input()", "ввод от пользователя", "преобразование типов"],
        7: ["if", "else", "elif", "условия", "сравнения ==, !=, <, >"],
        8: ["for", "while", "циклы", "range()"],
        9: ["списки", "[]", "append()", "индексы"],
        10: ["функции", "def", "return", "параметры"],
        11: ["словари", "{}", "ключи", "значения"],
        12: ["try", "except", "обработка ошибок"],
        13: ["open()", "read()", "write()", "файлы"],
        14: ["модули", "import", "библиотеки"]
    }
    
    @staticmethod
    async def ask_gpt4free(prompt: str) -> str:
        """Запрос к GPT через g4f."""
        try:
            response = g4f.ChatCompletion.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}]
            )
            return response
        except Exception as e:
            logging.error(f"GPT request failed: {e}")
            return "⌛ Ошибка при генерации контента. Попробуйте позже."
    
    @staticmethod
    def get_allowed_concepts(topic_num: int) -> str:
        """Получает разрешенные концепции для урока."""
        allowed = []
        for i in range(1, topic_num + 1):
            if i in GPTService.TOPIC_CONCEPTS:
                allowed.extend(GPTService.TOPIC_CONCEPTS[i])
        return ", ".join(allowed)
    
    @staticmethod
    async def generate_lesson(topic: str, course_type: str) -> str:
        """Генерирует урок по теме."""
        course_name = "Python" if course_type == "python" else "Aiogram"
        
        prompt = f"""
        Создай урок по теме "{topic}" для изучения {course_name}.
        
        КРИТИЧЕСКИ ВАЖНО! НЕ ИСПОЛЬЗУЙ HTML ТЕГИ ВООБЩЕ! 
        Используй только:
        - **жирный текст** для выделения
        - Эмодзи для структуры
        - Обычный текст без тегов
        
        Структура:
        💡 Что это такое?
        [простое объяснение концепции]
        
        💻 Примеры кода:
        print("Hello World")
        # комментарий к коду
        
        ⚡ Важные моменты:
        [ключевые советы и особенности]
        
        🎯 Что запомнить:
        [краткие выводы]
        
        НЕ ИСПОЛЬЗУЙ <b>, <i>, <code>, <pre> и другие HTML теги!
        Максимум 1800 символов.
        Делай урок понятным и структурированным.
        """
        
        response = await GPTService.ask_gpt4free(prompt)
        
        # Преобразуем **текст** в <b>текст</b>
        response = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', response)
        
        # Оборачиваем код в теги (строки которые выглядят как код)
        lines = response.split('\n')
        formatted_lines = []
        
        for line in lines:
            # Если строка выглядит как код Python
            if (line.strip().startswith(('print(', 'input(', 'if ', 'for ', 'while ', 'def ')) 
                or '=' in line and not line.startswith(('💡', '💻', '⚡', '🎯', '#'))
                or line.strip().startswith('#')):
                formatted_lines.append(f'<code>{line}</code>')
            else:
                formatted_lines.append(line)
        
        return '\n'.join(formatted_lines)
    
    @staticmethod
    async def generate_task(topic: str, topic_num: int, studied_topics: list) -> str:
        """Генерирует практическое задание по теме."""
        allowed_concepts = GPTService.get_allowed_concepts(topic_num)
        
        prompt = f"""
        Создай ПРОСТОЕ практическое задание по теме "{topic}" (урок номер {topic_num}).
        
        СТРОГИЕ ОГРАНИЧЕНИЯ:
        - Используй ТОЛЬКО эти изученные концепции: {allowed_concepts}
        - НЕ используй неизученные темы (input, if, циклы, функции, списки и т.д.)
        - Задание должно быть выполнимо ТОЛЬКО с изученным материалом
        - Для урока 1-2: только print() и переменные
        - Для урока 3-5: добавляй типы данных и операции
        - И так далее по порядку
        
        ВАЖНО! НЕ ИСПОЛЬЗУЙ HTML ТЕГИ!
        Используй только:
        - **жирный** для выделения  
        - Эмодзи для структуры
        - Обычный текст
        
        Формат:
        🎯 **ЗАДАНИЕ:**
        [что нужно сделать - ПРОСТАЯ задача]
        
        📝 **ТРЕБОВАНИЯ:**
        [как должна работать программа - БЕЗ сложностей]
        
        💡 **ПОДСКАЗКА:**
        [небольшая помощь с использованием ТОЛЬКО изученного]
        
        Пример для урока 1: "Выведи приветствие и свое имя"
        Пример для урока 2: "Создай переменную с именем и выведи ее"
        
        Максимум 800 символов. НЕ усложняй задание!
        """
        
        response = await GPTService.ask_gpt4free(prompt)
        
        # Преобразуем **текст** в <b>текст</b>
        response = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', response)
        
        return response
    
    @staticmethod
    async def check_solution(task: str, solution: str, studied_topics: list, topic_num: int) -> str:
        """Проверяет решение задачи."""
        allowed_concepts = GPTService.get_allowed_concepts(topic_num)
        
        prompt = f"""
        Проверь решение студента для урока номер {topic_num}.
        
        Задача: {task}
        Решение студента: {solution}
        Разрешенные концепции: {allowed_concepts}
        
        КРИТЕРИИ ОЦЕНКИ:
        - Решение использует ТОЛЬКО изученные концепции
        - Код работает и решает задачу
        - Если студент использует неизученные концепции - снижай оценку
        
        ВАЖНО! НЕ ИСПОЛЬЗУЙ HTML ТЕГИ!
        Используй только:
        - **жирный** для выделения
        - Эмодзи для структуры
        - Обычный текст
        
        НЕ предлагай неизученные концепции в советах!
        
        Формат:
        🏆 **ОЦЕНКА:** ОТЛИЧНО/ХОРОШО/УДОВЛЕТВОРИТЕЛЬНО/ТРЕБУЕТ ДОРАБОТКИ
        
        💬 **АНАЛИЗ:**
        [что сделано правильно, что можно улучшить]
        
        💡 **СОВЕТ:**
        [как улучшить, используя ТОЛЬКО изученные концепции]
        
        Если использованы неизученные концепции - обязательно укажи это!
        Максимум 1000 символов.
        """
        
        response = await GPTService.ask_gpt4free(prompt)
        
        # Преобразуем **текст** в <b>текст</b>
        response = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', response)
        
        return response