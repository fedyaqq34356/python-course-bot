from aiogram import types, F
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from agreement import AgreementHandler

from states import StudyStates, CourseSelection
from keyboards import get_main_keyboard, get_course_selection_keyboard, get_topics_keyboard
from utils import safe_send_message, split_long_message
from gpt_service import GPTService
from course_manager import CourseManager

# Инициализируем менеджер курсов
course_manager = CourseManager()

async def start_handler(message: types.Message):
    """Обработчик команды /start."""
    # Регистрируем пользователя
    course_manager.register_user(
        message.from_user.id,
        message.from_user.username,
        message.from_user.first_name,
        message.from_user.last_name
    )
    
    # Инициализируем обработчик соглашений
    agreement_handler = AgreementHandler()
    
    # Проверяем, принял ли пользователь соглашение
    if not agreement_handler.has_accepted_agreement(message.from_user.id):
        # Показываем пользовательское соглашение
        agreement_text = agreement_handler.get_agreement_text()
        keyboard = agreement_handler.get_agreement_keyboard()
        
        await message.answer(
            agreement_text,
            parse_mode="HTML",
            reply_markup=keyboard
        )
        return
    
    # Если соглашение принято, показываем приветствие
    welcome_text = (
        "👋 <b>Велком ту май бот виз нейм Бот на коленке</b>\n\n"
        "Он даст вам базовые понятия, после если захотите могу вам тут скидывать задания для практики кототые уже не входят в прогарму обучение но имеют все ваши темы:\n"
        "🐍 <b>Python</b> — от основ до продвинутых тем\n"
        "🤖 <b>Aiogram</b> — создание Telegram ботов\n\n"
        "🎯 <b>Что коленка умеет:</b>\n"
        "• Генерировать интерактивные уроки\n"
        "• Создавать практические задания\n"
        "• Проверять ваши решения\n"
        "• Отслеживать прогресс обучения\n\n"
        "📚 <b>Порядок изучения:</b>\n"
        "1. Сначала изучите Python (основы)\n"
        "2. Затем переходите к Aiogram (создание ботов)\n\n"
        "Выберите действие в меню ниже! 👇"
    )
    
    await message.answer(
        welcome_text,
        parse_mode="HTML",
        reply_markup=get_main_keyboard()
    )

async def course_selection_handler(message: types.Message):
    """Обработчик выбора курса."""
    keyboard = get_course_selection_keyboard()
    
    # Проверяем доступ к Aiogram курсу
    can_access_aiogram = course_manager.can_access_aiogram(message.from_user.id)
    
    if not can_access_aiogram:
        # Если Python не завершен, блокируем Aiogram
        keyboard.inline_keyboard[1][0].text = "🔒 Курс Aiogram (завершите Python)"
        keyboard.inline_keyboard[1][0].callback_data = "course_locked"
    
    await message.answer(
        "📚 <b>Выберите курс для изучения:</b>\n\n"
        "🐍 <b>Python</b> — основы программирования\n"
        "🤖 <b>Aiogram</b> — создание Telegram ботов\n\n"
        "💡 <b>Рекомендация:</b> Начните с Python, если вы новичок!",
        parse_mode="HTML",
        reply_markup=keyboard
    )

async def show_progress(message: types.Message):
    """Показывает общий прогресс пользователя."""
    progress_text = course_manager.format_full_progress(message.from_user.id)
    await message.answer(progress_text, parse_mode="HTML")

async def show_help(message: types.Message):
    """Показывает справку по использованию бота."""
    help_text = (
        "ℹ️ <b>Помощь по использованию бота:</b>\n\n"
        "📚 <b>Выбрать курс</b> — выбор между Python и Aiogram\n"
        "📊 <b>Мой прогресс</b> — статистика обучения\n\n"
        "💡 <b>Как проходить уроки:</b>\n"
        "1. Изучите теорию\n"
        "2. Получите практическое задание\n"
        "3. Напишите код построчно\n"
        "4. Отправьте команду /ready когда закончите\n"
        "5. Получите обратную связь от бота\n\n"
        "📋 <b>Структура обучения:</b>\n"
        "• Python курс: 14 тем (основы программирования)\n"
        "• Aiogram курс: 10 тем (создание ботов)\n\n"
        "🔒 <b>Доступ к Aiogram:</b> Сначала завершите Python курс\n\n"
        "🤖 Бот использует GPT для генерации уроков!"
    )
    await message.answer(help_text, parse_mode="HTML")

async def agreement_callback_handler(callback: types.CallbackQuery):
    """Обработчик callback для пользовательского соглашения."""
    agreement_handler = AgreementHandler()
    
    if callback.data == "accept_agreement":
        # Пользователь принял соглашение
        agreement_handler.accept_agreement(callback.from_user.id)
        
        # Сначала удаляем старое сообщение
        await callback.message.delete()
        
        welcome_text = (
            "✅ <b>Соглашение принято!</b>\n\n"
            "👋 <b>Велком ту май бот виз нейм Бот на коленке</b>\n\n"
            "Он даст вам базовые понятия, после если захотите могу вам тут скидывать задания для практики кототые уже не входят в прогарму обучение но имеют все ваши темы!\n"
            "🐍 <b>Python</b> — от основ до продвинутых тем\n"
            "🤖 <b>Aiogram</b> — создание Telegram ботов\n\n"
            "🎯 <b>Что коленка умеет:</b>\n"
            "• Генерировать интерактивные уроки\n"
            "• Создавать практические задания\n"
            "• Проверять ваши решения\n"
            "• Отслеживать прогресс обучения\n\n"
            "📚 <b>Порядок изучения:</b>\n"
            "1. Сначала изучите Python (основы)\n"
            "2. Затем переходите к Aiogram (создание ботов)\n\n"
            "Выберите действие в меню ниже! 👇"
        )
        
        # Отправляем новое сообщение с reply клавиатурой
        await callback.message.answer(
            welcome_text,
            parse_mode="HTML",
            reply_markup=get_main_keyboard()
        )
        
    elif callback.data == "decline_agreement":
        # Пользователь отклонил соглашение
        await callback.message.edit_text(
            "❌ <b>Соглашение отклонено</b>\n\n"
            "К сожалению, без принятия пользовательского соглашения "
            "вы не можете использовать бота.\n\n"
            "Для повторного просмотра соглашения отправьте команду /start",
            parse_mode="HTML"
        )


async def course_callback_handler(callback: types.CallbackQuery):
    """Обработчик выбора курса."""
    if callback.data == "course_locked":
        await callback.answer("🔒 Завершите курс Python для доступа к Aiogram!", show_alert=True)
        return
    
    course_type = callback.data.split("_")[1]  # python или aiogram
    user_id = callback.from_user.id
    
    if course_type == "aiogram" and not course_manager.can_access_aiogram(user_id):
        await callback.answer("🔒 Завершите курс Python для доступа к Aiogram!", show_alert=True)
        return
    
    # Показываем список тем курса
    topics_text = course_manager.format_topics_list(user_id, course_type)
    keyboard = get_topics_keyboard(
        user_id, 
        course_manager.get_topics(course_type), 
        course_manager.get_user_progress(user_id, course_type),
        course_type
    )
    
    course_name = "Python" if course_type == "python" else "Aiogram"
    
    study_info = (
        f"\n\n📖 <b>Выберите тему для изучения:</b>\n\n"
        f"✅ - Тема изучена\n"
        f"🔄 - Доступна для изучения\n"
        f"⏳ - Пока недоступна"
    )
    
    full_text = topics_text + study_info
    
    await callback.message.edit_text(
        full_text,
        parse_mode="HTML",
        reply_markup=keyboard
    )

async def study_topic_callback(callback: types.CallbackQuery, state: FSMContext):
    """Обработчик изучения темы."""
    # Парсим callback: study_python_1 или study_aiogram_1
    parts = callback.data.split("_")
    course_type = parts[1]  # python или aiogram
    topic_num = int(parts[2])  # номер темы
    
    user_id = callback.from_user.id
    
    # Проверяем доступность темы
    progress = course_manager.get_user_progress(user_id, course_type)
    if topic_num > progress + 1:
        await callback.answer("⌛ Эта тема пока недоступна!", show_alert=True)
        return
    
    # Проверяем доступ к Aiogram курсу
    if course_type == "aiogram" and not course_manager.can_access_aiogram(user_id):
        await callback.answer("🔒 Завершите курс Python для доступа к Aiogram!", show_alert=True)
        return
    
    topics = course_manager.get_topics(course_type)
    topic = topics[topic_num - 1]
    
    await callback.message.edit_text(
        f"📖 <b>Урок {topic_num}: {topic}</b>\n\n"
        "🔄 Генерирую урок, подождите...",
        parse_mode="HTML"
    )
    
    # Генерируем урок
    lesson = await GPTService.generate_lesson(topic, course_type)
    
    lesson_text = (
        f"📖 <b>УРОК {topic_num}: {topic}</b>\n\n"
        f"{lesson}\n\n"
        "📝 Нажмите кнопку ниже, чтобы получить практическое задание!"
    )
    
    task_button = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📝 Получить задание", callback_data=f"task_{course_type}_{topic_num}")]
    ])
    
    # Разбиваем длинное сообщение если нужно
    if len(lesson_text) > 4096:
        parts = split_long_message(lesson_text)
        
        for i, part in enumerate(parts):
            if i == 0:
                await safe_send_message(callback.message, part, parse_mode="HTML")
            else:
                await safe_send_message(callback.message, part, parse_mode="HTML")
        
        # Отправляем кнопку для задания отдельно
        await safe_send_message(
            callback.message,
            "📝 <b>Готовы перейти к практике?</b>",
            parse_mode="HTML",
            reply_markup=task_button
        )
    else:
        await safe_send_message(
            callback.message,
            lesson_text,
            parse_mode="HTML", 
            reply_markup=task_button
        )

async def get_task_callback(callback: types.CallbackQuery, state: FSMContext):
    """Обработчик получения задания."""
    # Парсим callback: task_python_1 или task_aiogram_1
    parts = callback.data.split("_")
    course_type = parts[1]
    topic_num = int(parts[2])
    
    topics = course_manager.get_topics(course_type)
    topic = topics[topic_num - 1]
    studied_topics = topics[:topic_num]  # Изученные темы
    
    await callback.message.edit_text(
        f"🎯 <b>Практическое задание по теме {topic_num}</b>\n\n"
        "🔄 Генерирую задание...",
        parse_mode="HTML"
    )
    
    # Генерируем задание
    task = await GPTService.generate_task(topic, topic_num, studied_topics)
    
    task_text = (
        f"🎯 <b>ПРАКТИЧЕСКОЕ ЗАДАНИЕ {topic_num}</b>\n\n"
        f"{task}\n\n"
        "💻 <b>Как отправить решение:</b>\n"
        "1. Напишите код построчно в чат\n"
        "2. Когда закончите, отправьте команду /ready\n"
        "3. Получите обратную связь от бота!"
    )
    
    # Разбиваем длинное задание если нужно
    if len(task_text) > 4096:
        parts = split_long_message(task_text)
        for i, part in enumerate(parts):
            if i == 0:
                await safe_send_message(callback.message, part, parse_mode="HTML")
            else:
                await safe_send_message(callback.message, part, parse_mode="HTML")
    else:
        await safe_send_message(callback.message, task_text, parse_mode="HTML")
    
    # Сохраняем контекст в состоянии
    await state.update_data(
        course_type=course_type,
        topic_num=topic_num,
        task=task,
        solution_lines=[]
    )
    await state.set_state(StudyStates.waiting_for_solution)




async def check_solution_handler(message: types.Message, state: FSMContext):
    """Проверка решения задачи."""
    data = await state.get_data()
    solution_lines = data.get("solution_lines", [])
    
    if not solution_lines:
        await message.answer(
            "⌛ Вы не отправили код!\n"
            "Напишите код построчно, затем отправьте /ready"
        )
        return
    
    solution = "\n".join(solution_lines)
    task = data.get("task", "")
    topic_num = data.get("topic_num", 1)
    course_type = data.get("course_type", "python")
    
    topics = course_manager.get_topics(course_type)
    studied_topics = topics[:topic_num]
    
    await message.answer(
        "🔍 <b>Проверяю ваше решение...</b>\n"
        "⏳ Подождите немного...",
        parse_mode="HTML"
    )
    
    # Проверяем решение
    feedback = await GPTService.check_solution(task, solution, studied_topics, topic_num)
    # Сохраняем решение в базу данных
    course_manager.save_solution(
        message.from_user.id,
        course_type,
        topic_num,
        task,
        solution,
        feedback
    )

    
    feedback_text = (
        f"📋 <b>РЕЗУЛЬТАТ ПРОВЕРКИ</b>\n\n"
        f"{feedback}\n\n"
        f"🎉 Тема {topic_num} завершена!"
    )
    
    # Разбиваем длинную обратную связь если нужно
    if len(feedback_text) > 4096:
        parts = split_long_message(feedback_text)
        for part in parts:
            await safe_send_message(message, part, parse_mode="HTML")
    else:
        await safe_send_message(message, feedback_text, edit=False, parse_mode="HTML")
    
    # Обновляем прогресс
    course_manager.update_user_progress(message.from_user.id, course_type, topic_num)
    
    # Проверяем завершение курса
    total_topics = len(topics)
    if topic_num == total_topics:
        course_name = "Python" if course_type == "python" else "Aiogram"
        completion_text = (
            f"🏆 <b>ПОЗДРАВЛЯЕМ!</b>\n\n"
            f"Вы успешно завершили курс {course_name}!\n"
            f"Изучено тем: {total_topics}/{total_topics}\n\n"
        )
        
        if course_type == "python":
            completion_text += (
                "🤖 <b>Что дальше?</b>\n"
                "Теперь вам доступен курс Aiogram для создания Telegram ботов!\n\n"
                "Используйте команду 📚 Выбрать курс, чтобы начать изучение Aiogram."
            )
        else:
            completion_text += (
                "🎊 Вы освоили создание Telegram ботов!\n"
                "Теперь вы можете создавать собственных ботов на Python + Aiogram."
            )
        
        await message.answer(completion_text, parse_mode="HTML")
    
    # Очищаем состояние
    await state.clear()

async def collect_solution(message: types.Message, state: FSMContext):
    """Сбор строк решения."""
    data = await state.get_data()
    solution_lines = data.get("solution_lines", [])
    solution_lines.append(message.text)
    
    await state.update_data(solution_lines=solution_lines)
    
    # Подтверждаем получение строки кода
    await message.reply(
        f"✅ Строка {len(solution_lines)} добавлена\n"
        "Продолжайте писать код или отправьте /ready"
    )

