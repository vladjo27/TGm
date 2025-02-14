# Personal Task Manager Bot

[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python Version](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/release/python-380/)
[![Telegram Bot](https://img.shields.io/badge/Telegram-Bot-blue.svg)](https://telegram.org)

Personal Task Manager Bot - это телеграм-бот, который помогает вам организовать свои задачи и напоминания. С его помощью вы можете добавлять задачи в различные категории, отмечать их как выполненные, удалять и изменять категории.

## Основные функции

### 1. Добавление задачи
**Описание:** Добавьте новую задачу в выбранную категорию.
- **Пример использования:** Нажмите на кнопку "📝 Добавить задачу" и следуйте инструкциям бота. Например, вы можете ввести "Работа" как категорию и "Сдать отчет" как задачу.

### 2. Просмотр задач
**Описание:** Просмотрите все ваши задачи, сгруппированные по категориям.
- **Пример использования:** Нажмите на кнопку "📋 Показать задачи". Бот покажет все ваши задачи, разделенные по категориям, например:
📂 Ваши задачи:

📁 Работа
❌ Сдать отчет
❌ Заказать пиццу

📁 Учеба
❌ Подготовиться к экзамену

### 3. Удаление задачи
**Описание:** Удалите задачу из выбранной категории.
- **Пример использования:** Нажмите на кнопку "❌ Удалить задачу", выберите категорию и затем номер задачи. Например, если у вас есть задача "Сдать отчет" в категории "Работа", выберите категорию "Работа" и введите "1" для удаления этой задачи.

### 4. Очистка всех задач
**Описание:** Удалите все задачи за один раз.
- **Пример использования:** Нажмите на кнопку "🧹 Очистить все задачи". Бот запросит подтверждение и удалит все ваши задачи.

### 5. Изменение категории задачи
**Описание:** Переместите задачу в другую категорию.
- **Пример использования:** Нажмите на кнопку "📦 Изменить категорию", выберите категорию и номер задачи, затем выберите новую категорию. Например, переместите задачу "Сдать отчет" из категории "Работа" в категорию "Личное".

### 6. Просмотр завершенных задач
**Описание:** Просмотрите завершенные задачи.
- **Пример использования:** Нажмите на кнопку "✅ Завершенные задачи". Бот покажет все завершенные задачи, например:
- 🎉 Завершенные задачи:

▫️ Работа
└ ✅ Сдать отчет

### 7. Отметка выполнения задачи
**Описание:** Отметьте задачу как выполненную или неполную.
- **Пример использования:** Нажмите на кнопку "✔️ Отметить выполнение", выберите категорию и номер задачи. Например, отметьте задачу "Подготовиться к экзамену" как выполненную.

### 8. Перезапуск бота
**Описание:** Перезапустите бота для сброса состояния.
- **Пример использования:** Нажмите на кнопку "🔄 Перезапустить". Бот перезапустится, и вы вернетесь к начальному меню.

## Установка

1. Клонируйте репозиторий:

 ```bash
 git clone https://github.com/yourusername/personal-task-manager-bot.git
 cd personal-task-manager-bot

Установите необходимые зависимости:
pip install aiogram sqlite3
Создайте файл .env в корневой директории проекта и добавьте токен вашего бота:
BOT_TOKEN=YOUR_BOT_API_TOKEN_HERE
Запустите бота:
python bot.py
Использование
Команды бота
/start: Начните работу с ботом и получите доступ к основному меню.
📝 Добавить задачу: Добавьте новую задачу в выбранную категорию.
📋 Показать задачи: Просмотрите все ваши задачи, сгруппированные по категориям.
❌ Удалить задачу: Удалите задачу из выбранной категории.
🧹 Очистить все задачи: Удалите все задачи за один раз.
📦 Изменить категорию: Переместите задачу в другую категорию.
✅ Завершенные задачи: Просмотрите завершенные задачи.
✔️ Отметить выполнение: Отметьте задачу как выполненную или неполную.
🔄 Перезапустить: Перезапустите бота.
Пример работы
Нажмите /start для начала работы с ботом.
Выберите действие из предложенного меню.
Следуйте инструкциям бота для выполнения выбранного действия.
Вклад
Ваш вклад в развитие этого проекта очень ценен! Если у вас есть предложения по улучшению или вы нашли ошибку, пожалуйста, создайте issue или pull request.

Лицензия
Этот проект распространяется под лицензией MIT. Подробнее см. LICENSE .

Спасибо за использование Personal Task Manager Bot! Мы надеемся, что он поможет вам лучше организовать свои задачи и напоминания.
