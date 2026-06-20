from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

def get_main_keyboard() -> ReplyKeyboardMarkup:
    """Создает главную клавиатуру."""
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📚 Выбрать курс")],
            [KeyboardButton(text="📊 Мой прогресс")],
            [KeyboardButton(text="ℹ️ Помощь")]
        ],
        resize_keyboard=True,
        one_time_keyboard=False
    )
    return keyboard

def get_course_selection_keyboard() -> InlineKeyboardMarkup:
    """Создает клавиатуру для выбора курса."""
    buttons = [
        [InlineKeyboardButton(text="🐍 Курс Python", callback_data="course_python")],
        [InlineKeyboardButton(text="🤖 Курс Aiogram", callback_data="course_aiogram")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_topics_keyboard(user_id: int, topics: list, progress: int, course_type: str) -> InlineKeyboardMarkup:
    """Создает клавиатуру с темами."""
    buttons = []
    
    for i, topic in enumerate(topics, 1):
        if i <= progress + 1:  # Доступны изученные + следующая тема
            status = "✅" if i <= progress else "🔄"
            button_text = f"{status} {i}. {topic[:25]}..."
            buttons.append([InlineKeyboardButton(
                text=button_text,
                callback_data=f"study_{course_type}_{i}"
            )])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)