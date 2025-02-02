import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder
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

# Список задач с категориями и процентами выполнения (в реальном проекте лучше использовать базу данных)
tasks = {}

# Состояния для FSM (Finite State Machine)
class TaskStates(StatesGroup):
    waiting_for_category = State()
    waiting_for_task = State()
    waiting_for_category_to_delete = State()
    waiting_for_task_to_delete = State()
    waiting_for_task_to_update_progress = State()
    waiting_for_progress_value = State()

# Команда /start
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    builder = ReplyKeyboardBuilder()
    builder.add(KeyboardButton(text="Добавить задачу"))
    builder.add(KeyboardButton(text="Показать задачи"))
    builder.add(KeyboardButton(text="Удалить задачу"))
    builder.add(KeyboardButton(text="Указать процент выполнения"))  # Добавляем кнопку
    await message.answer(
        "Привет! Я бот-планировщик. Что ты хочешь сделать?",
        reply_markup=builder.as_markup(resize_keyboard=True)
    )

# Обработка кнопки "Добавить задачу"
@dp.message(lambda message: message.text == "Добавить задачу")
async def add_task(message: types.Message, state: FSMContext):
    await message.answer("Введите категорию для задачи (например, Работа, Учёба, Личное):")
    await state.set_state(TaskStates.waiting_for_category)

# Обработка ввода категории
@dp.message(TaskStates.waiting_for_category)
async def process_category(message: types.Message, state: FSMContext):
    category = message.text.strip()
    if category not in tasks:
        tasks[category] = []  # Создаём новую категорию, если её нет
    await state.update_data(category=category)  # Сохраняем категорию в состоянии
    await message.answer(f"Категория '{category}' выбрана. Теперь введите задачу:")
    await state.set_state(TaskStates.waiting_for_task)

# Обработка ввода задачи
@dp.message(TaskStates.waiting_for_task)
async def process_task(message: types.Message, state: FSMContext):
    data = await state.get_data()
    category = data.get("category")
    task = message.text.strip()
    tasks[category].append({"task": task, "progress": 0})  # Добавляем задачу в категорию с начальным процентом выполнения 0
    await message.answer(f"Задача добавлена в категорию '{category}': {task}")
    await state.clear()

# Обработка кнопки "Показать задачи"
@dp.message(lambda message: message.text == "Показать задачи")
async def show_tasks(message: types.Message):
    if tasks:
        response = "Ваши задачи:\n"
        for category, task_list in tasks.items():
            if task_list:
                tasks_list = "\n".join([f"{i + 1}. {task['task']} ({task['progress']}%)" for i, task in enumerate(task_list)])
                response += f"\nКатегория: {category}\n{tasks_list}\n"
        await message.answer(response)
    else:
        await message.answer("Задач пока нет.")

# Обработка кнопки "Удалить задачу"
@dp.message(lambda message: message.text == "Удалить задачу")
async def delete_task(message: types.Message, state: FSMContext):
    if tasks:
        categories_list = "\n".join([f"{i + 1}. {category}" for i, category in enumerate(tasks.keys())])
        await message.answer(f"Выберите категорию для удаления задачи:\n{categories_list}")
        await state.set_state(TaskStates.waiting_for_category_to_delete)
    else:
        await message.answer("Задач пока нет.")

# Обработка ввода номера категории для удаления
@dp.message(TaskStates.waiting_for_category_to_delete)
async def process_category_to_delete(message: types.Message, state: FSMContext):
    try:
        category_number = int(message.text) - 1
        categories = list(tasks.keys())
        if 0 <= category_number < len(categories):
            category = categories[category_number]
            task_list = tasks[category]
            if task_list:
                tasks_list = "\n".join([f"{i + 1}. {task['task']} ({task['progress']}%)" for i, task in enumerate(task_list)])
                await message.answer(f"Введите номер задачи для удаления из категории '{category}':\n{tasks_list}")
                await state.update_data(category=category)  # Сохраняем категорию в состоянии
                await state.set_state(TaskStates.waiting_for_task_to_delete)
            else:
                await message.answer(f"В категории '{category}' задач нет.")
                await state.clear()
        else:
            await message.answer("Неверный номер категории.")
            await state.clear()
    except ValueError:
        await message.answer("Пожалуйста, введите число.")
        await state.clear()

# Обработка ввода номера задачи для удаления
@dp.message(TaskStates.waiting_for_task_to_delete)
async def process_task_number_to_delete(message: types.Message, state: FSMContext):
    try:
        task_number = int(message.text) - 1
        data = await state.get_data()
        category = data.get("category")
        task_list = tasks[category]
        if 0 <= task_number < len(task_list):
            removed_task = task_list.pop(task_number)
            await message.answer(f"Задача удалена из категории '{category}': {removed_task['task']}")
            if not task_list:  # Если в категории больше нет задач, удаляем её
                del tasks[category]
        else:
            await message.answer("Неверный номер задачи.")
            await state.clear()  # Очищаем состояние после ошибки
    except ValueError:
        await message.answer("Пожалуйста, введите число.")
        await state.clear()  # Очищаем состояние после ошибки

# Обработка кнопки "Указать процент выполнения"
@dp.message(lambda message: message.text == "Указать процент выполнения")
async def update_progress(message: types.Message, state: FSMContext):
    if tasks:
        categories_list = "\n".join([f"{i + 1}. {category}" for i, category in enumerate(tasks.keys())])
        await message.answer(f"Выберите категорию для обновления прогресса задачи:\n{categories_list}")
        await state.set_state(TaskStates.waiting_for_task_to_update_progress)
    else:
        await message.answer("Задач пока нет.")

# Обработка ввода номера категории для обновления прогресса
@dp.message(TaskStates.waiting_for_task_to_update_progress)
async def process_category_to_update_progress(message: types.Message, state: FSMContext):
    try:
        category_number = int(message.text) - 1
        categories = list(tasks.keys())
        if 0 <= category_number < len(categories):
            category = categories[category_number]
            task_list = tasks[category]
            if task_list:
                tasks_list = "\n".join([f"{i + 1}. {task['task']} ({task['progress']}%)" for i, task in enumerate(task_list)])
                await message.answer(f"Введите номер задачи для обновления прогресса в категории '{category}':\n{tasks_list}")
                await state.update_data(category=category)  # Сохраняем категорию в состоянии
                await state.set_state(TaskStates.waiting_for_progress_value)
            else:
                await message.answer(f"В категории '{category}' задач нет.")
                await state.clear()
        else:
            await message.answer("Неверный номер категории.")
            await state.clear()
    except ValueError:
        await message.answer("Пожалуйста, введите число.")
        await state.clear()

# Обработка ввода процента выполнения
@dp.message(TaskStates.waiting_for_progress_value)
async def process_progress_value(message: types.Message, state: FSMContext):
    try:
        progress = int(message.text)
        if 0 <= progress <= 100:
            data = await state.get_data()
            category = data.get("category")
            task_list = tasks[category]
            task_number = data.get("task_number")
            task_list[task_number]["progress"] = progress
            await message.answer(f"Прогресс задачи '{task_list[task_number]['task']}' обновлен до {progress}%.")
            await state.clear()
        else:
            await message.answer("Пожалуйста, введите число от 0 до 100.")
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
