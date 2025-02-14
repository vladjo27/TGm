import logging
import sqlite3
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from datetime import datetime, timedelta

# Настройка логирования
import logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


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

# После создания таблиц добавим проверку столбца is_completed
cursor.execute('PRAGMA table_info(tasks)')
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
    waiting_for_category_to_mark_complete = State()
    waiting_for_task_to_mark_complete = State()

# Функция для создания клавиатуры
def create_keyboard(buttons):
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=btn)] for btn in buttons],
        resize_keyboard=True
    )

async def check_state_timeout(state: FSMContext):
    data = await state.get_data()
    if 'last_activity' in data:
        last_activity = datetime.fromisoformat(data['last_activity'])
        if datetime.now() - last_activity > timedelta(minutes=5):
            await state.clear()
            return True
    return False

# Команда /start
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    user_id = message.from_user.id
    cursor.execute('INSERT OR IGNORE INTO users (user_id) VALUES (?)', (user_id,))
    conn.commit()
    keyboard = create_keyboard([
        "📝 Добавить задачу",
        "📋 Показать задачи",
        "❌ Удалить задачу",
        "🧹 Очистить все задачи",
        "📦 Изменить категорию",
        "✅ Завершенные задачи",
        "✔️ Отметить выполнение",
        "🔄 Перезапустить"
    ])
    await message.answer(
        "👋 Привет! Я твой персональный бот-планировщик!\n"
        "Выбери действие из меню ниже:",
        reply_markup=keyboard,
        parse_mode='HTML'
    )

@dp.message(lambda message: message.text == "🔄 Перезапустить")
async def restart_bot(message: types.Message):
    await cmd_start(message)
    
async def get_category(message: types.Message, state: FSMContext, next_state: State):
    if await check_state_timeout(state):
        await message.answer("⏳ Сессия истекла, начните заново.")
        return
    
    await state.update_data(last_activity=datetime.now().isoformat())

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
    try:
        logger.info(f"Entered get_task with state: {await state.get_state()}")

        # Проверяем активное состояние
        current_state = await state.get_state()
        if current_state is None:
            await message.answer("⚠️ Сессия устарела, начните операцию заново.")
            return

        # Получаем user_id из состояния
        data = await state.get_data()
        user_id = data.get("user_id")
        if not user_id:
            logger.error("User ID not found in state")
            await state.clear()
            await message.answer("❌ Ошибка сессии, начните заново.")
            return

        # Проверяем и преобразуем ввод пользователя
        try:
            category_number = int(message.text.strip()) - 1
        except ValueError:
            logger.warning("Invalid input - not a number")
            await message.answer("❌ Пожалуйста, введите <b>число</b> из списка.", parse_mode='HTML')
            await state.clear()
            return

        # Получаем список категорий
        cursor.execute('SELECT DISTINCT category FROM tasks WHERE user_id = ?', (user_id,))
        categories = [row[0] for row in cursor.fetchall()]
        
        if not categories:
            logger.warning("No categories found")
            await message.answer("❌ Категории не найдены.")
            await state.clear()
            return

        # Проверяем диапазон введенного номера
        if not (0 <= category_number < len(categories)):
            logger.warning(f"Invalid category number: {category_number + 1} (max {len(categories)})")
            await message.answer(f"❌ Неверный номер категории. Введите число от 1 до {len(categories)}")
            await state.clear()
            return

        category = categories[category_number]
        logger.info(f"Selected category: {category}")

        # Получаем задачи для категории
        cursor.execute('SELECT id, task FROM tasks WHERE user_id = ? AND category = ?', (user_id, category))
        task_list = cursor.fetchall()
        
        if not task_list:
            logger.warning(f"No tasks in category: {category}")
            await message.answer(f"📭 В категории <b>'{category}'</b> задач нет.", parse_mode='HTML')
            await state.clear()
            return

        # Формируем список задач
        tasks_list = "\n".join([f"{i + 1}. {task[1]}" for i, task in enumerate(task_list)])
        await message.answer(f"Выберите номер задачи:\n{tasks_list}")
        
        # Обновляем состояние
        await state.update_data(
            category=category,
            task_list=task_list,
            last_action=datetime.now().isoformat()
        )
        await state.set_state(next_state)
        logger.info(f"State updated to {next_state}")

    except sqlite3.Error as e:
        logger.error(f"Database error: {str(e)}")
        await message.answer("⚠️ Ошибка базы данных. Попробуйте позже.")
        await state.clear()
        
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        await message.answer("⚠️ Непредвиденная ошибка. Начните заново.")
        await state.clear()

# Обработка кнопки "Добавить задачу"
@dp.message(lambda message: message.text == "📝 Добавить задачу")
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
        await message.answer(f"🎯 Категория <b>'{category}'</b> уже существует. Введи новую задачу:",
        parse_mode='HTML')
    else:
        # Если категории нет, сообщаем, что она будет создана
        await message.answer(f"🎉 Создана новая категория <b>'{category}'</b>! Теперь введи задачу:",
        parse_mode='HTML')
    
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
    cursor.execute('INSERT INTO tasks (user_id, category, task) VALUES (?, ?, ?)', (user_id, category, task))
    conn.commit()
    await message.answer(f"✅ Задача успешно добавлена в категорию <b>'{category}'</b>:\n"
        f"▫️ <i>{task}</i>",
        parse_mode='HTML')
    await state.clear()

# Обработка кнопки "Показать задачи"
@dp.message(lambda message: message.text == "📋 Показать задачи")
async def show_tasks(message: types.Message):
    user_id = message.from_user.id
    cursor.execute('SELECT category, task, is_completed FROM tasks WHERE user_id = ?', (user_id,))
    tasks = cursor.fetchall()
    
    if tasks:
        # Группируем задачи по категориям
        tasks_by_category = {}
        for category, task, is_completed in tasks:
            if category not in tasks_by_category:
                tasks_by_category[category] = []
            tasks_by_category[category].append((task, is_completed))
        
        # Формируем ответ
        response = "📂 Ваши задачи:\n\n"
        for category, tasks_list in tasks_by_category.items():
            response += f"📁 <b>{category}</b>\n"
            for task, is_completed in tasks_list:
                status_emoji = "✅" if is_completed else "❌"
                response += f"  └ {status_emoji} {task}\n"
            response += "\n"
        
        await message.answer(response, parse_mode='HTML')
    else:
        await message.answer("Задач пока нет.")

@dp.errors()
async def errors_handler(update: types.Update, exception: Exception):
    logger.error(f"Global error: {exception}")
    return True

# Обработка кнопки "Удалить задачу"
@dp.message(lambda message: message.text == "❌ Удалить задачу")
async def delete_task(message: types.Message, state: FSMContext):
    await get_category(message, state, TaskStates.waiting_for_category_to_delete)

# Обработка ввода номера категории для удаления
@dp.message(TaskStates.waiting_for_category_to_delete)
async def process_category_to_delete(message: types.Message, state: FSMContext):
    await get_task(message, state, TaskStates.waiting_for_task_to_delete)

# Обработка ввода номера задачи для удаления
@dp.message(TaskStates.waiting_for_task_to_delete)
async def process_task_number_to_delete(message: types.Message, state: FSMContext):
    try:
        if await state.get_state() != TaskStates.waiting_for_task_to_delete:
            await message.answer("⚠️ Сессия устарела, начните заново")
            await state.clear()
            return

        user_id = (await state.get_data()).get("user_id")
        task_number = int(message.text) - 1
        data = await state.get_data()
        category = data.get("category")
        task_list = data.get("task_list")
        
        if 0 <= task_number < len(task_list):
            task_id = task_list[task_number][0]
            cursor.execute('DELETE FROM tasks WHERE id = ?', (task_id,))
            conn.commit()
            await message.answer(f"🗑 Задача из категории <b>'{category}'</b> успешно удалена!", parse_mode='HTML')
        else:
            await message.answer("Неверный номер задачи.")
        
        await state.clear()  # Всегда очищаем состояние после обработки

    except ValueError:
        await message.answer("Пожалуйста, введите число.")
        await state.clear()
    except Exception as e:
        logger.error(f"Ошибка: {e}")
        await message.answer("⚠️ Произошла ошибка, попробуйте снова.")
        await state.clear()

# Обработка кнопки "Очистить все задачи"
@dp.message(lambda message: message.text == "🧹 Очистить все задачи")
async def clear_all_tasks(message: types.Message):
    user_id = message.from_user.id
    cursor.execute('DELETE FROM tasks WHERE user_id = ?', (user_id,))
    conn.commit()
    await message.answer("🚮 Все задачи успешно удалены")

# Обработка кнопки "Изменить категорию задачи"
@dp.message(lambda message: message.text == "📦 Изменить категорию")
async def change_task_category(message: types.Message, state: FSMContext):
    await get_category(message, state, TaskStates.waiting_for_category_to_change)

# Обработка ввода номера категории для изменения
@dp.message(TaskStates.waiting_for_category_to_change)
async def process_category_to_change(message: types.Message, state: FSMContext):
    await get_task(message, state, TaskStates.waiting_for_task_to_change_category)

# Обработка ввода номера задачи для изменения категории
@dp.message(TaskStates.waiting_for_task_to_change_category)
async def process_task_number_to_change_category(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    logging.info(f"Текущее состояние: {current_state}")

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
            logging.info(f"Неверный номер задачи: {task_number}. Очищаем состояние.")
            await state.clear()  # Очищаем состояние при ошибке
            await message.answer("Неверный номер задачи.")
    except ValueError:
        logging.info("Пользователь ввел не число. Очищаем состояние.")
        await state.clear()  # Очищаем состояние при ошибке
        await message.answer("Пожалуйста, введите число.")

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
    await message.answer( f"🔀 Задача перемещена:\n"
        f"▫️ Из категории <b>'{old_category}'</b>\n"
        f"▫️ В категорию <b>'{new_category}'</b>",
        parse_mode='HTML')
    await state.clear()

# Обработка кнопки "Показать завершенные задачи"
@dp.message(lambda message: message.text == "✅ Завершенные задачи")
async def show_completed_tasks(message: types.Message):
    user_id = message.from_user.id
    cursor.execute('SELECT category, task FROM tasks WHERE user_id = ? AND is_completed = 1', (user_id,))
    completed_tasks = cursor.fetchall()
    if completed_tasks:
        response = "🎉 Завершенные задачи:\n\n"
        for category, task in completed_tasks:
            response += f"▫️ <b>{category}</b>\n  └ ✅ {task}\n"
        await message.answer(response,
        parse_mode='HTML')
    else:
        await message.answer("Завершенных задач пока нет.")

# Обработка кнопки "Отметить задачу завершенной"
@dp.message(lambda message: message.text == "✔️ Отметить выполнение")
async def mark_task_complete_start(message: types.Message, state: FSMContext):
    await get_category(message, state, TaskStates.waiting_for_category_to_mark_complete)

# Обработка выбора категории для отметки выполнения
@dp.message(TaskStates.waiting_for_category_to_mark_complete)
async def process_category_to_mark_complete(message: types.Message, state: FSMContext):
    await get_task(message, state, TaskStates.waiting_for_task_to_mark_complete)

# Обработка выбора задачи для отметки выполнения
@dp.message(TaskStates.waiting_for_task_to_mark_complete)
async def process_task_to_mark_complete(message: types.Message, state: FSMContext):
    user_id = (await state.get_data()).get("user_id")
    try:
        task_number = int(message.text) - 1
        data = await state.get_data()
        category = data.get("category")
        task_list = data.get("task_list")
        
        if 0 <= task_number < len(task_list):
            task_id = task_list[task_number][0]
            
            # Проверяем текущий статус задачи
            cursor.execute('SELECT task, is_completed FROM tasks WHERE id = ?', (task_id,))
            task_text, current_status = cursor.fetchone()
            
            # Инвертируем статус
            new_status = 1 if current_status == 0 else 0
            status_emoji = "✅" if new_status == 1 else "❌"
            
            cursor.execute('UPDATE tasks SET is_completed = ? WHERE id = ?', 
                         (new_status, task_id))
            conn.commit()
            
            await message.answer(f"{status_emoji} Статус задачи обновлен!\n"
        f"▫️ Категория: <b>{category}</b>\n"
        f"▫️ Задача: <i>{task_text}</i>\n"
        f"▫️ Новый статус: {'Выполнено' if new_status else 'Не выполнено'}",
        parse_mode='HTML')
            await state.clear()  # Очищаем состояние после успешного обновления
        else:
            await state.clear()  # Очищаем состояние при ошибке
            await message.answer("Неверный номер задачи.")
            
    except ValueError:
        await message.answer("Пожалуйста, введите число.")
        await state.clear()  # Очищаем состояние при ошибке
    except Exception as e:
        logging.error(f"Ошибка: {e}")
        await message.answer("⚠️ Произошла ошибка, попробуйте снова.")
        await state.clear()  # Очищаем состояние при ошибке

@dp.message()
async def unhandled_message(message: types.Message):
    await message.answer(
        "⚠️ Не понимаю команду. Используйте кнопки меню.",
        reply_markup=create_keyboard([
            "📝 Добавить задачу",
            "📋 Показать задачи",
            "🔄 Перезапустить"
        ])
    )

# Запуск бота
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
