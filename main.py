исправь код, он не работает 
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
import tempfile
from dataclasses import dataclass
from enum import Enum, auto

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Токен вашего бота
BOT_TOKEN = '7730408777:AAEHH8vZcpXIAAH0n5zz6-J3Fw_TkrU7gOg'

# Инициализация бота и диспетчера
bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

# Словарь для хранения задач с категориями и процентами выполнения для каждого пользователя
user_tasks = {}

# Состояния для FSM (Finite State Machine)
class TaskStates(StatesGroup):
    waiting_for_category = State()
    waiting_for_task = State()
    waiting_for_category_to_delete = State()
    waiting_for_task_to_delete = State()
    waiting_for_task_to_update_progress = State()
    waiting_for_progress_value = State()
    waiting_for_category_to_change = State()
    waiting_for_task_to_change_category = State()
    waiting_for_new_category = State()

@dataclass
class Task:
    task: str
    progress: int = 0

class Actions(Enum):
    ADD_TASK = auto()
    SHOW_TASKS = auto()
    DELETE_TASK = auto()
    UPDATE_PROGRESS = auto()
    SHOW_STATISTICS = auto()
    CLEAR_ALL_TASKS = auto()
    EXPORT_TASKS = auto()
    CHANGE_TASK_CATEGORY = auto()
    SHOW_COMPLETED_TASKS = auto()

# Команда /start
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    user_id = message.from_user.id
    if user_id not in user_tasks:
        user_tasks[user_id] = {}
    
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Добавить задачу")],
            [KeyboardButton(text="Показать задачи")],
            [KeyboardButton(text="Удалить задачу")],
            [KeyboardButton(text="Указать процент выполнения")],
            [KeyboardButton(text="Показать статистику задач")],
            [KeyboardButton(text="Очистить все задачи")],
            [KeyboardButton(text="Экспорт задач")],
            [KeyboardButton(text="Изменить категорию задачи")],
            [KeyboardButton(text="Показать завершенные задачи")]
        ],
        resize_keyboard=True
    )
    await message.answer(
        "Привет! Я бот-планировщик. Что ты хочешь сделать?",
        reply_markup=keyboard
    )

async def get_category(message: types.Message, state: FSMContext, next_state: State):
    user_id = message.from_user.id
    if user_id in user_tasks and user_tasks[user_id]:
        categories_list = "\n".join([f"{i + 1}. {category}" for i, category in enumerate(user_tasks[user_id].keys())])
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
        categories = list(user_tasks[user_id].keys())
        if 0 <= category_number < len(categories):
            category = categories[category_number]
            task_list = user_tasks[user_id][category]
            if task_list:
                tasks_list = "\n".join([f"{i + 1}. {task.task} ({task.progress}%)" for i, task in enumerate(task_list)])
                await message.answer(f"Введите номер задачи:\n{tasks_list}")
                await state.update_data(category=category)
                await state.set_state(next_state)
            else:
                await message.answer(f"В категории '{category}' задач нет.")
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
    if category not in user_tasks[user_id]:
        user_tasks[user_id][category] = []
    await state.update_data(category=category)
    await message.answer(f"Категория '{category}' выбрана. Теперь введите задачу:")
    await state.set_state(TaskStates.waiting_for_task)

# Обработка ввода задачи
@dp.message(TaskStates.waiting_for_task)
async def process_task(message: types.Message, state: FSMContext):
    user_id = (await state.get_data()).get("user_id")
    data = await state.get_data()
    category = data.get("category")
    task = Task(task=message.text.strip())
    user_tasks[user_id][category].append(task)
    await message.answer(f"Задача добавлена в категорию '{category}': {task.task}")
    await state.clear()

# Обработка кнопки "Показать задачи"
@dp.message(lambda message: message.text == "Показать задачи")
async def show_tasks(message: types.Message):
    user_id = message.from_user.id
    if user_id in user_tasks and user_tasks[user_id]:
        response = "Ваши задачи:\n"
        for category, task_list in user_tasks[user_id].items():
            if task_list:
                tasks_list = "\n".join([f"{i + 1}. {task.task} ({task.progress}%)" for i, task in enumerate(task_list)])
                response += f"\nКатегория: {category}\n{tasks_list}\n"
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
        task_list = user_tasks[user_id][category]
        if 0 <= task_number < len(task_list):
            removed_task = task_list.pop(task_number)
            await message.answer(f"Задача удалена из категории '{category}': {removed_task.task}")
            if not task_list:
                del user_tasks[user_id][category]
        else:
            await message.answer("Неверный номер задачи.")
            await state.clear()
    except ValueError:
        await message.answer("Пожалуйста, введите число.")
        await state.clear()

# Обработка кнопки "Указать процент выполнения"
@dp.message(lambda message: message.text == "Указать процент выполнения")
async def update_progress(message: types.Message, state: FSMContext):
    await get_category(message, state, TaskStates.waiting_for_task_to_update_progress)

# Обработка ввода номера категории для обновления прогресса
@dp.message(TaskStates.waiting_for_task_to_update_progress)
async def process_category_to_update_progress(message: types.Message, state: FSMContext):
    await get_task(message, state, TaskStates.waiting_for_progress_value)

# Обработка ввода процента выполнения
@dp.message(TaskStates.waiting_for_progress_value)
async def process_progress_value(message: types.Message, state: FSMContext):
    user_id = (await state.get_data()).get("user_id")
    try:
        progress = int(message.text)
        if 0 <= progress <= 100:
            data = await state.get_data()
            category = data.get("category")
            task_list = user_tasks[user_id][category]
            task_number = data.get("task_number")
            task_list[task_number].progress = progress
            await message.answer(f"Прогресс задачи '{task_list[task_number].task}' обновлен до {progress}%.")
            await state.clear()
        else:
            await message.answer("Пожалуйста, введите число от 0 до 100.")
            await state.clear()
    except ValueError:
        await message.answer("Пожалуйста, введите число.")
        await state.clear()

# Обработка кнопки "Показать статистику задач"
@dp.message(lambda message: message.text == "Показать статистику задач")
async def show_statistics(message: types.Message):
    user_id = message.from_user.id
    if user_id in user_tasks and user_tasks[user_id]:
        response = "Статистика задач:\n"
        for category, task_list in user_tasks[user_id].items():
            total_tasks = len(task_list)
            completed_tasks = sum(1 for task in task_list if task.progress == 100)
            response += f"\nКатегория: {category}\nВсего задач: {total_tasks}\nЗавершено: {completed_tasks}\n"
        await message.answer(response)
    else:
        await message.answer("Задач пока нет.")

# Обработка кнопки "Очистить все задачи"
@dp.message(lambda message: message.text == "Очистить все задачи")
async def clear_all_tasks(message: types.Message):
    user_id = message.from_user.id
    if user_id in user_tasks:
        user_tasks[user_id].clear()
    await message.answer("Все задачи и категории удалены.")

# Обработка кнопки "Экспорт задач"
@dp.message(lambda message: message.text == "Экспорт задач")
async def export_tasks(message: types.Message):
    user_id = message.from_user.id
    if user_id in user_tasks and user_tasks[user_id]:
        export_text = "Ваши задачи:\n"
        for category, task_list in user_tasks[user_id].items():
            if task_list:
                tasks_list = "\n".join([f"{i + 1}. {task.task} ({task.progress}%)" for i, task in enumerate(task_list)])
                export_text += f"\nКатегория: {category}\n{tasks_list}\n"
        with tempfile.NamedTemporaryFile(mode='w+', suffix='.txt', delete=False) as temp_file:
            temp_file.write(export_text)
            temp_file.seek(0)
            await message.answer_document(types.InputFile(temp_file.name, filename="tasks.txt"))
    else:
        await message.answer("Задач пока нет.")

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
        task_list = user_tasks[user_id][category]
        if 0 <= task_number < len(task_list):
            task_to_move = task_list[task_number]
            await message.answer(f"Выберите новую категорию для задачи '{task_to_move.task}':")
            await state.update_data(task_to_move=task_to_move, old_category=category, task_number=task_number)
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
    task_to_move = data.get("task_to_move")
    old_category = data.get("old_category")
    task_number = data.get("task_number")
    if new_category not in user_tasks[user_id]:
        user_tasks[user_id][new_category] = []
    user_tasks[user_id][new_category].append(task_to_move)
    user_tasks[user_id][old_category].pop(task_number)
    if not user_tasks[user_id][old_category]:
        del user_tasks[user_id][old_category]
    await message.answer(f"Задача '{task_to_move.task}' перемещена в категорию '{new_category}'.")
    await state.clear()

# Обработка кнопки "Показать завершенные задачи"
@dp.message(lambda message: message.text == "Показать завершенные задачи")
async def show_completed_tasks(message: types.Message):
    user_id = message.from_user.id
    if user_id in user_tasks and user_tasks[user_id]:
        response = "Завершенные задачи:\n"
        for category, task_list in user_tasks[user_id].items():
            completed_tasks = [task for task in task_list if task.progress == 100]
            if completed_tasks:
                tasks_list = "\n".join([f"{i + 1}. {task.task} ({task.progress}%)" for i, task in enumerate(completed_tasks)])
                response += f"\nКатегория: {category}\n{tasks_list}\n"
        await message.answer(response)
    else:
        await message.answer("Задач пока нет.")

# Запуск бота
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
