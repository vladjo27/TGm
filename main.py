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

# Список задач (в реальном проекте лучше использовать базу данных)
tasks = []

# Состояния для FSM (Finite State Machine)
class TaskStates(StatesGroup):
    waiting_for_task = State()
    waiting_for_task_to_delete = State()

# Команда /start
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    builder = ReplyKeyboardBuilder()
    builder.add(KeyboardButton(text="Добавить задачу"))
    builder.add(KeyboardButton(text="Показать задачи"))
    builder.add(KeyboardButton(text="Удалить задачу"))
    await message.answer(
        "Привет! Я бот-планировщик. Что ты хочешь сделать?",
        reply_markup=builder.as_markup(resize_keyboard=True)
    )

# Обработка кнопки "Добавить задачу"
@dp.message(lambda message: message.text == "Добавить задачу")
async def add_task(message: types.Message, state: FSMContext):
    await message.answer("Введите задачу:")
    await state.set_state(TaskStates.waiting_for_task)

# Обработка ввода задачи
@dp.message(TaskStates.waiting_for_task)
async def process_task(message: types.Message, state: FSMContext):
    tasks.append(message.text)
    await message.answer(f"Задача добавлена: {message.text}")
    await state.clear()

# Обработка кнопки "Показать задачи"
@dp.message(lambda message: message.text == "Показать задачи")
async def show_tasks(message: types.Message):
    if tasks:
        tasks_list = "\n".join([f"{i + 1}. {task}" for i, task in enumerate(tasks)])
        await message.answer(f"Ваши задачи:\n{tasks_list}")
    else:
        await message.answer("Задач пока нет.")

# Обработка кнопки "Удалить задачу"
@dp.message(lambda message: message.text == "Удалить задачу")
async def delete_task(message: types.Message, state: FSMContext):
    if tasks:
        tasks_list = "\n".join([f"{i + 1}. {task}" for i, task in enumerate(tasks)])
        await message.answer(f"Введите номер задачи для удаления:\n{tasks_list}")
        await state.set_state(TaskStates.waiting_for_task_to_delete)
    else:
        await message.answer("Задач пока нет.")

# Обработка ввода номера задачи для удаления
@dp.message(TaskStates.waiting_for_task_to_delete)
async def process_task_to_delete(message: types.Message, state: FSMContext):
    try:
        task_number = int(message.text) - 1
        if 0 <= task_number < len(tasks):
            removed_task = tasks.pop(task_number)
            await message.answer(f"Задача удалена: {removed_task}")
        else:
            await message.answer("Неверный номер задачи.")
    except ValueError:
        await message.answer("Пожалуйста, введите число.")
    await state.clear()

# Запуск бота
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
