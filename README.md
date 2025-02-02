📅 Бот Планировщик Задач
Этот бот является простым планировщиком задач, созданным с использованием библиотеки aiogram для Telegram. Он позволяет пользователю добавлять, удалять, обновлять и отслеживать выполнение задач по категориям.

🚀 Функциональность
Бот предоставляет следующие возможности:

Добавление задач с указанием категории и описания задачи.
Показ задач по категориям, включая процент выполнения каждой задачи.
Удаление задач: пользователь может выбрать категорию и удалить задачу.
Обновление прогресса задачи: позволяет указать процент выполнения задачи.
Показ статистики задач: отображает количество задач в каждой категории и сколько из них завершены.
Очистка всех задач: удаляет все задачи и категории.
Экспорт задач: позволяет экспортировать список всех задач в текстовый файл.
Изменение категории задачи: позволяет перемещать задачу в другую категорию.
Показ завершенных задач: отображает задачи, которые полностью выполнены (100% прогресса).
🛠️ Технологии
aiogram: асинхронная библиотека для работы с Telegram API.
FSM (Finite State Machine): для управления состоянием пользователя и обработки шагов в диалогах.
MemoryStorage: хранение данных в памяти для работы с состояниями FSM (для тестовых целей или небольших проектов).
📝 Установка
Клонируйте репозиторий:

bash
Copy code
git clone https://github.com/ваш-репозиторий.git
cd ваш-репозиторий
Установите зависимости:

bash
Copy code
pip install -r requirements.txt
Добавьте свой токен в код:
В файле bot.py замените BOT_TOKEN = 'Og' на ваш собственный токен, который можно получить у BotFather.

Запустите бота:

bash
Copy code
python bot.py
💡 Использование
Основные команды:
/start — Запуск бота и отображение главного меню.
Добавить задачу — Создание новой задачи с выбором категории.
Показать задачи — Отображение всех текущих задач.
Удалить задачу — Удаление задачи из категории.
Указать процент выполнения — Обновление прогресса задачи.
Показать статистику задач — Информация о числе задач и завершенных задачах в каждой категории.
Очистить все задачи — Удаление всех задач.
Экспорт задач — Скачивание списка задач в текстовый файл.
Изменить категорию задачи — Перемещение задачи в другую категорию.
Показать завершенные задачи — Отображение задач с 100% прогрессом.

## 📝 Основные команды

### 1. **/start**
- **Что делает**:  
  При старте бот приветствует пользователя и предлагает выбрать одну из доступных опций.
  
- **Как работает**:  
  Бот генерирует клавиатуру с несколькими кнопками:  
  - **Добавить задачу**  
  - **Показать задачи**  
  - **Удалить задачу**  
  - **Указать процент выполнения**  
  - **Показать статистику задач**  
  - **Очистить все задачи**  
  - **Экспорт задач**  
  - **Изменить категорию задачи**  
  - **Показать завершенные задачи**  

  Выбор кнопки запускает соответствующую команду бота.

---

### 2. **Добавить задачу**
- **Что делает**:  
  Позволяет пользователю добавить новую задачу в выбранную категорию.

- **Как работает**:  
  Бот попросит ввести **категорию** (например, "Работа", "Учёба", "Личное").  
  Если категория не существует, бот создаст её.  
  Затем бот запросит **описание задачи**, например, "Написать отчет". Задача будет добавлена в выбранную категорию с начальным прогрессом 0%.

---

### 3. **Показать задачи**
- **Что делает**:  
  Отображает все задачи, которые пользователь добавил в разные категории, а также показывает процент выполнения каждой задачи.

- **Как работает**:  
  Бот выводит список всех категорий с задачами в каждой из них. Для каждой задачи отображается её название и текущий процент выполнения.

  Пример:
  ```
  Категория: Работа
  1. Написать отчет (40%)
  2. Позвонить клиенту (100%)

  Категория: Личное
  1. Пойти в спортзал (25%)
  ```

  Если задач нет, бот сообщит об этом.

---

### 4. **Удалить задачу**
- **Что делает**:  
  Позволяет удалить задачу из выбранной категории.

- **Как работает**:  
  Бот предложит выбрать категорию, из которой вы хотите удалить задачу.  
  Затем бот покажет список задач в этой категории и попросит ввести номер задачи, которую нужно удалить.  
  После подтверждения задача будет удалена. Если в категории не осталось задач, она также будет удалена.

---

### 5. **Указать процент выполнения**
- **Что делает**:  
  Позволяет обновить процент выполнения задачи в выбранной категории.

- **Как работает**:  
  Бот предложит выбрать категорию, затем список задач в ней.  
  После этого пользователь выбирает задачу и указывает новый процент выполнения (от 0 до 100%).

  Например, если задача была выполнена на 40%, а пользователь вводит 60%, прогресс будет обновлен.

---

### 6. **Показать статистику задач**
- **Что делает**:  
  Отображает статистику по задачам в каждой категории: сколько всего задач и сколько из них завершено.

- **Как работает**:  
  Бот выводит для каждой категории информацию о:
  - Общее количество задач.
  - Количество завершенных задач (с 100% прогрессом).

  Пример:
  ```
  Статистика задач:
  Категория: Работа
  Всего задач: 3
  Завершено: 1

  Категория: Личное
  Всего задач: 2
  Завершено: 0
  ```

---

### 7. **Очистить все задачи**
- **Что делает**:  
  Удаляет все задачи и категории из базы данных бота.

- **Как работает**:  
  При выборе этой команды все задачи и категории будут полностью удалены. Бот подтвердит, что все данные очищены.

  Это может быть полезно, если вы хотите начать с нуля.

---

### 8. **Экспорт задач**
- **Что делает**:  
  Экспортирует все задачи в текстовый файл, который можно скачать.

- **Как работает**:  
  Бот создает текстовый файл, в котором содержится список всех задач с указанием категорий и прогресса. Этот файл будет отправлен пользователю в виде вложения, которое можно скачать.

  Пример содержимого файла:
  ```
  Ваши задачи:
  Категория: Работа
  1. Написать отчет (40%)
  2. Позвонить клиенту (100%)

  Категория: Личное
  1. Пойти в спортзал (25%)
  ```

---

### 9. **Изменить категорию задачи**
- **Что делает**:  
  Позволяет переместить задачу из одной категории в другую.

- **Как работает**:  
  Бот предложит выбрать категорию и задачу, которую вы хотите переместить. Затем пользователь вводит новую категорию для задачи. Задача будет перемещена в новую категорию, а старая категория будет удалена, если в ней не осталось задач.

  Например, задача "Написать отчет" перемещается из категории "Личное" в "Работа".

---

### 10. **Показать завершенные задачи**
- **Что делает**:  
  Отображает только те задачи, которые завершены на 100%.

- **Как работает**:  
  Бот покажет только те задачи, которые имеют прогресс 100%. Это поможет пользователю увидеть, что уже сделано, и как много задач завершены.

  Пример:
  ```
  Завершенные задачи:
  Категория: Работа
  1. Позвонить клиенту (100%)

  Категория: Личное
  1. Прочитать книгу (100%)
  ```



