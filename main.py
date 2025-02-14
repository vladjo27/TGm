import logging
import sqlite3
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Токен вашего бота
BOT_TOKEN = '7730408777:AAEHH8vZcpXIAAH0n5zz6-J3Fw_TkrU7gOg'

# Инициализация бота и диспетчера
bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

# Подключение к базе данных
conn = sqlite3.connect('tasks.db', check_same_thread=False)
cursor = conn.cursor()

# Создание таблиц
cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY
)
''')
cursor.execute('''
CREATE TABLE IF NOT EXISTS tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    category TEXT,
    task TEXT,
    is_completed INTEGER DEFAULT 0,
    FOREIGN KEY (user_id) REFERENCES users (user_id)
)
''')
conn.commit()

# Проверка наличия столбца is_completed и его добавление, если его нет
cursor.execute("PRAGMA table_info(tasks)")
columns = [column[1] for column in cursor.fetchall()]
if 'is_completed' not in columns:
    cursor.execute('ALTER TABLE tasks ADD COLUMN is_completed INTEGER DEFAULT 0')
conn.commit()

# Состояния для FSM (Finite State Machine)
class TaskStates(StatesGroup):
    waiting_for_category = State()
    waiting_for_task = State()
    waiting_for_category_to_delete = State()
    waiting_for_task_to_delete = State()
    waiting_for_category_to_change = State()
    waiting_for_task_to_change_category = State()
    waiting_for_new_category = State()
    waiting_for_task_to_select = State()
    waiting_for_task_to_mark_complete = State()

# Функция для создания клавиатуры
def create_keyboard(buttons):
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=btn)] for btn in buttons],
        resize_keyboard=True
    )

# Команда /start
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    user_id = message.from_user.id
    cursor.execute('INSERT OR IGNORE INTO users (user_id) VALUES (?)', (user_id,))
    conn.commit()
    keyboard = create_keyboard([
        "Добавить задачу",
        "Показать задачи",
        "Удалить задачу",
        "Показать статистику задач",
        "Очистить все задачи",
        "Изменить категорию задачи",
        "Показать завершенные задачи",
        "Отметить задачу завершенной"
    ])
    await message.answer(
        "Привет! Я бот-планировщик. Что ты хочешь сделать?",
        reply_markup=keyboard
    )

async def get_category(message: types.Message, state: FSMContext, next_state: State):
    user_id = message.from_user.id
    cursor.execute('SELECT DISTINCT category FROM tasks WHERE user_id = ?', (user_id,))
    categories = cursor.fetchall()
    if categories:
        categories_list = "\n".join([f"{i + 1}. {category[0]}" for i, category in enumerate(categories)])
        await message.answer(f"Выберите категорию:\n{categories_list}")
        await state.set_state(next_state)
        await state.update_data(user_id=user_id)
    else:
        await message.answer("Задач пока нет.")
        await state.clear()

async def get_task(message: types.Message, state: FSMContext, next_state: State):
    user_id = (await state.get_data()).get("user_id")
    try:
        category_number = int(message.text) - 1
        cursor.execute('SELECT DISTINCT category FROM tasks WHERE user_id = ?', (user_id,))
        categories = cursor.fetchall()
        if 0 <= category_number < len(categories):
            category = categories[category_number][0]
            cursor.execute('SELECT id, task FROM tasks WHERE user_id = ? AND category = ? AND is_completed = 0', (user_id, category))
            task_list = cursor.fetchall()
            if task_list:
                tasks_list = "\n".join([f"{i + 1}. {task[1]}" for i, task in enumerate(task_list)])
                await message.answer(f"Введите номер задачи:\n{tasks_list}")
                await state.update_data(category=category, task_list=task_list)
                await state.set_state(next_state)
            else:
                await message.answer(f"В категории '{category}' нет незавершенных задач.")
                await state.clear()
        else:
            await message.answer("Неверный номер категории.")
            await state.clear()
    except ValueError:
        await message.answer("Пожалуйста, введите число.")
        await state.clear()

# Обработка кнопки "Добавить задачу"
@dp.message(lambda message: message.text == "Добавить задачу")
async def add_task(message: types.Message, state: FSMContext):
    await message.answer("Введите категорию для задачи (например, Работа, Учёба, Личное):")
    await state.set_state(TaskStates.waiting_for_category)
    await state.update_data(user_id=message.from_user.id)

# Обработка ввода категории
@dp.message(TaskStates.waiting_for_category)
async def process_category(message: types.Message, state: FSMContext):
    user_id = (await state.get_data()).get("user_id")
    category = message.text.strip()
    # Проверяем, существует ли такая категория для данного пользователя
    cursor.execute('SELECT DISTINCT category FROM tasks WHERE user_id = ?', (user_id,))
    categories = [row[0] for row in cursor.fetchall()]
    if category in categories:
        # Если категория уже существует, используем её
        await message.answer(f"Категория '{category}' уже существует. Теперь введите задачу:")
    else:
        # Если категории нет, сообщаем, что она будет создана
        await message.answer(f"Создана новая категория '{category}'. Теперь введите задачу:")
    # Обновляем состояние и переходим к вводу задачи
    await state.update_data(category=category)
    await state.set_state(TaskStates.waiting_for_task)

# Обработка ввода задачи
@dp.message(TaskStates.waiting_for_task)
async def process_task(message: types.Message, state: FSMContext):
    user_id = (await state.get_data()).get("user_id")
    data = await state.get_data()
    category = data.get("category")
    task = message.text.strip()
    # Проверяем, существует ли такая категория для данного пользователя
    cursor.execute('SELECT DISTINCT category FROM tasks WHERE user_id = ?', (user_id,))
    categories = [row[0] for row in cursor.fetchall()]
    if category not in categories:
        # Если категории нет, создаем её
        await message.answer(f"Создана новая категория '{category}'.")
    # Добавляем задачу в категорию
    cursor.execute('INSERT INTO tasks (user_id, category, task, is_completed) VALUES (?, ?, ?, 0)', (user_id, category, task))
    conn.commit()
    await message.answer(f"Задача добавлена в категорию '{category}': {task}")
    await state.clear()

# Обработка кнопки "Показать задачи"
@dp.message(lambda message: message.text == "Показать задачи")
async def show_tasks(message: types.Message):
    user_id = message.from_user.id
    cursor.execute('SELECT category, task FROM tasks WHERE user_id = ?', (user_id,))
    tasks = cursor.fetchall()
    if tasks:
        # Группируем задачи по категориям
        tasks_by_category = {}
        for category, task in tasks:
            if category not in tasks_by_category:
                tasks_by_category[category] = []
            tasks_by_category[category].append(task)
        # Формируем ответ
        response = "Ваши задачи:\n"
        for category, tasks_list in tasks_by_category.items():
            response += f"\nКатегория: {category}\n"
            for task in tasks_list:
                response += f"- {task}\n"
        await message.answer(response)
    else:
        await message.answer("Задач пока нет.")

# Обработка кнопки "Удалить задачу"
@dp.message(lambda message: message.text == "Удалить задачу")
async def delete_task(message: types.Message, state: FSMContext):
    await get_category(message, state, TaskStates.waiting_for_category_to_delete)

# Обработка ввода номера категории для удаления
@dp.message(TaskStates.waiting_for_category_to_delete)
async def process_category_to_delete(message: types.Message, state: FSMContext):
    await get_task(message, state, TaskStates.waiting_for_task_to_delete)

# Обработка ввода номера задачи для удаления
@dp.message(TaskStates.waiting_for_task_to_delete)
async def process_task_number_to_delete(message: types.Message, state: FSMContext):
    user_id = (await state.get_data()).get("user_id")
    try:
        task_number = int(message.text) - 1
        data = await state.get_data()
        category = data.get("category")
        task_list = data.get("task_list")
        if 0 <= task_number < len(task_list):
            task_id = task_list[task_number][0]
            cursor.execute('DELETE FROM tasks WHERE id = ?', (task_id,))
            conn.commit()
            await message.answer(f"Задача удалена из категории '{category}'.")
        else:
            await message.answer("Неверный номер задачи.")
            await state.clear()
    except ValueError:
        await message.answer("Пожалуйста, введите число.")
        await state.clear()

# Обработка кнопки "Показать статистику задач"
@dp.message(lambda message: message.text == "Показать статистику задач")
async def show_statistics(message: types.Message):
    user_id = message.from_user.id
    cursor.execute('SELECT category, COUNT(*) AS total FROM tasks WHERE user_id = ? GROUP BY category', (user_id,))
    statistics = cursor.fetchall()
    if statistics:
        response = "Статистика задач:\n"
        for category, total in statistics:
            response += f"\nКатегория: {category}\nВсего задач: {total}\n"
        await message.answer(response)
    else:
        await message.answer("Задач пока нет.")

# Обработка кнопки "Очистить все задачи"
@dp.message(lambda message: message.text == "Очистить все задачи")
async def clear_all_tasks(message: types.Message):
    user_id = message.from_user.id
    cursor.execute('DELETE FROM tasks WHERE user_id = ?', (user_id,))
    conn.commit()
    await message.answer("Все задачи удалены.")

# Обработка кнопки "Изменить категорию задачи"
@dp.message(lambda message: message.text == "Изменить категорию задачи")
async def change_task_category(message: types.Message, state: FSMContext):
    await get_category(message, state, TaskStates.waiting_for_category_to_change)

# Обработка ввода номера категории для изменения
@dp.message(TaskStates.waiting_for_category_to_change)
async def process_category_to_change(message: types.Message, state: FSMContext):
    await get_task(message, state, TaskStates.waiting_for_task_to_change_category)

# Обработка ввода номера задачи для изменения категории
@dp.message(TaskStates.waiting_for_task_to_change_category)
async def process_task_number_to_change_category(message: types.Message, state: FSMContext):
    user_id = (await state.get_data()).get("user_id")
    try:
        task_number = int(message.text) - 1
        data = await state.get_data()
        category = data.get("category")
        task_list = data.get("task_list")
        if 0 <= task_number < len(task_list):
            task_id = task_list[task_number][0]
            cursor.execute('SELECT task FROM tasks WHERE id = ?', (task_id,))
            task_to_move = cursor.fetchone()[0]
            await message.answer(f"Выберите новую категорию для задачи '{task_to_move}':")
            await state.update_data(task_id=task_id, task_to_move=task_to_move, old_category=category)
            await state.set_state(TaskStates.waiting_for_new_category)
        else:
            await message.answer("Неверный номер задачи.")
            await state.clear()
    except ValueError:
        await message.answer("Пожалуйста, введите число.")
        await state.clear()

# Обработка ввода новой категории для задачи
@dp.message(TaskStates.waiting_for_new_category)
async def process_new_category(message: types.Message, state: FSMContext):
    user_id = (await state.get_data()).get("user_id")
    new_category = message.text.strip()
    data = await state.get_data()
    task_id = data.get("task_id")
    old_category = data.get("old_category")
    cursor.execute('UPDATE tasks SET category = ? WHERE id = ?', (new_category, task_id))
    conn.commit()
    await message.answer(f"Задача '{data.get('task_to_move')}' перемещена в категорию '{new_category}'.")
    await state.clear()

# Обработка кнопки "Показать завершенные задачи"
@dp.message(lambda message: message.text == "Показать завершенные задачи")
async def show_completed_tasks(message: types.Message):
    user_id = message.from_user.id
    cursor.execute('SELECT category, task FROM tasks WHERE user_id = ? AND is_completed = 1', (user_id,))
    completed_tasks = cursor.fetchall()
    if completed_tasks:
        response = "Завершенные задачи:\n"
        for category, task in completed_tasks:
            response += f"\nКатегория: {category}\nЗадача: {task}\n"
        await message.answer(response)
    else:
        await message.answer("Завершенных задач пока нет.")

# Обработка кнопки "Отметить задачу завершенной"
@dp.message(lambda message: message.text == "Отметить задачу завершенной")
async def mark_task_complete(message: types.Message, state: FSMContext):
    await get_category(message, state, TaskStates.waiting_for_task_to_mark_complete)

# Обработка ввода номера категории для отметки задачи завершенной
@dp.message(TaskStates.waiting_for_task_to_mark_complete)
async def process_task_number_to_mark_complete(message: types.Message, state: FSMContext):
    user_id = (await state.get_data()).get("user_id")
    try:
        task_number = int(message.text) - 1
        data = await state.get_data()
        category = data.get("category")
        task_list = data.get("task_list")
        logging.info(f"Category: {category}, Task List: {task_list}")
        if task_list is None:
            await message.answer(f"В категории '{category}' нет незавершенных задач.")
            await state.clear()
            return
        if 0 <= task_number < len(task_list):
            task_id = task_list[task_number][0]
            # Проверяем, была ли задача уже завершена
            cursor.execute('SELECT is_completed FROM tasks WHERE id = ?', (task_id,))
            is_completed = cursor.fetchone()[0]
            if is_completed:
                await message.answer("Эта задача уже была завершена.")
            else:
                # Отмечаем задачу как завершенную
                cursor.execute('UPDATE tasks SET is_completed = 1 WHERE id = ?', (task_id,))
                conn.commit()
                await message.answer(f"Задача отмечена как завершенная.")
        else:
            await message.answer("Неверный номер задачи.")
            await state.clear()
    except ValueError:
        await message.answer("Пожалуйста, введите число.")
        await state.clear()

# Запуск бота
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
