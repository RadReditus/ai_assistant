
# ai_assistant
telegram bot + google sheets API + GPT API + Promting + python
=======
# bot-assistant
```
bot-assistant — это Telegram-бот, который автоматизирует процесс сбора данных от потенциальных клиентов (лидов) для компании, помогающей студентам поступать за рубеж. Бот запрашивает у пользователя ФИО, номер телефона и страну интереса, сохраняет данные в Google Таблицу, отправляет уведомление менеджерам в Telegram-группу и поддерживает распознавание голосовых сообщений с преобразованием в текст.

Основные функции
Сбор данных: Запрашивает у пользователя ФИО, номер телефона и страну интереса через текстовые или голосовые сообщения.
Сохранение данных: Сохраняет собранные данные в Google Таблицу через Google Sheets API.
Уведомления: Отправляет сообщение в Telegram-группу менеджеров о новом лиде.
Распознавание голоса: Преобразует голосовые сообщения в текст с помощью SpeechRecognition и Google Speech-to-Text API.
Логирование: Поддерживает логирование по уровням критичности (INFO, WARNING, ERROR) для отладки и мониторинга.
Чистый код и расширяемость: Код организован по принципам чистого кода, с модульной архитектурой, что упрощает добавление новых функций (например, новых полей или интеграций с CRM).
Промптинг: Использует промпты для взаимодействия с пользователем, которые можно легко настраивать через конфигурационные файлы.
```
# Used technologies
```
Python 3.10+
together: AI модель + применение промтинга
aiogram: Библиотека для создания Telegram-ботов.
Google Sheets API: Для сохранения данных лидов.
SpeechRecognition: Для распознавания голосовых сообщений.
ffmpeg: Для конвертации аудиофайлов (OGG в WAV).
logging: Для логирования по уровням критичности.
subprocess: Для безопасного вызова ffmpeg.
pydantic: Для валидации данных (опционально, если добавляется строгая типизация).
```

## Clone project
```
git clone https://github.com/radik-karimov/bot-assistant.git
cd bot-assistant
```

## Project setup
```
pip install -r requirements.txt

aiogram
google-api-python-client
google-auth-httplib2
google-auth-oauthlib
speechrecognition
pydub (для работы с аудиофайлами)
python-dotenv (для работы с переменными окружения)

```
## Project utilits
```
Установите ffmpeg:

- Windows:
Скачайте ffmpeg с gyan.dev.
Распакуйте в C:\ffmpeg.
Добавьте C:\ffmpeg\bin в PATH.

ffmpeg -version
- Linux:

sudo apt-get install ffmpeg


- macOS:

brew install ffmpeg
```
### Setting ENVIROMENT
```
Создайте файл .env в корне проекта:
env


-TELEGRAM_BOT_TOKEN=your-telegram-bot-token
-GOOGLE_SHEETS_CREDENTIALS_PATH=path/to/credentials.json
-MANAGERS_GROUP_CHAT_ID=your-managers-group-chat-id



TELEGRAM_BOT_TOKEN: Токен вашего Telegram-бота (получите через @BotFather).
GOOGLE_SHEETS_CREDENTIALS_PATH: Путь к файлу credentials.json для Google Sheets API.
MANAGERS_GROUP_CHAT_ID: ID Telegram-группы менеджеров (можно получить через @getidsbot).

______________________
Настройте Google Sheets API:

Создайте проект в Google Cloud Console.
Включите Google Sheets API.
Создайте учетные данные (Service Account) и скачайте файл credentials.json.
Укажите путь к credentials.json в .env.
Создайте Google Таблицу и дайте доступ вашему Service Account (email из credentials.json).
```

### Setting file .env
```
Main fields of file:

GOOGLE_SHEET_DATAS = ./config/example-google-credentials.json
GOOGLE_SPREADSHEET_ID = example_spreadsheet_id
SCOPES = https://www.googleapis.com/auth/spreadsheets
AI_TOKEN = example_ai_token
AI_MODEL = example-ai/model-name

TG_BOT_TOKEN = example_bot_token
TG_GROUP_ID = example_group_id
LINK_TG_BOT = t.me/example_bot_link

TEST_GOOGLE_SHEET_DATAS = ./config/example-google-credentials.json
TEST_GOOGLE_SPREADSHEET_ID = example_test_spreadsheet_id
TEST_SCOPES = https://www.googleapis.com/auth/spreadsheets

DEBUG = True
```


### Compiles and hot-reloads for development
```
python main.py

Убедитесь что все зависимости в .env установлены
```
### Structure of project
```
bot-assistant/
├── main.py                 # Точка входа
├── handlers/              # Обработчики сообщений
│   ├── __init__.py
│   ├── client.py          # Логика обработки данных клиента
│   └── other.py           # Обработка остальных сообщений
├── services/              # Сервисы и утилиты
│   ├── __init__.py
│   ├── gpt.py             # Логика работы с промптами
│   ├── config.py          # Конфигурация промптов
│   ├── sheet_worker.py    # Работа с Google Sheets
│   ├── logger_func.py     # Настройка логирования
│   └── manage_msgs.py     # Отправка сообщений менеджерам
├── .env                   # Переменные окружения
├── requirements.txt       # Зависимости
└── README.md              # Документация
```

### Dialog example
```
Пример диалога
Пользователь:

/start
Бот:

Привет! Как вас зовут полностью?
Пользователь:

(голосовое сообщение: "Иванов Иван Иванович")
Бот:

Отлично, Иван Иванович! Какой у вас номер телефона?
Пользователь:

+79991234567
Бот:

Спасибо! В какой стране хотите учиться?
Пользователь:

Канада
Бот:

Готово! Давайте посмотрим, что у нас:
1 - Иванов Иван Иванович
2 - +79991234567
3 - Канада
Менеджерам в группу:

Новый лид в гугл таблице
Иванов Иван Иванович
+79991234567
Канада
Пример сохранённых данных
Данные сохраняются в Google Таблицу с колонками:

ФИО	Телефон	Страна	Дата и время
Иванов Иван Иванович	+79991234567	Канада	2025-04-01 07:38:15


```

### Logs
```
Логирование настроено с уровнями критичности:

INFO: Информация о процессе (например, "Получен file_id", "Распознанный текст").
WARNING: Предупреждения (например, "Не найдено голосовое сообщение").
ERROR: Ошибки (например, "Ошибка при обработке аудиофайла").
Логи выводятся в консоль и могут быть настроены для записи в файл через logger_func.py.

Чистый код и расширяемость
Модульная архитектура: Код разделён на модули (handlers, services), что упрощает добавление новых функций.
Промптинг: Промпты хранятся в services/config.py и могут быть легко изменены или расширены.
Расширяемость:
Легко добавить новые поля в форму, просто добавив новые состояния в ClientForm.
Поддержка других CRM-систем (например, Bitrix24) может быть реализована через новый класс в services.
Чистота кода:
Используются аннотации типов.
Обработка ошибок через try-except.
Логирование для отладки.
```

### Deploy
```
Проект можно развернуть на любом сервере с Python, например:


Создайте Procfile:
web: python main.py


Разверните через heroku git:push.

1 VPS (например, DigitalOcean):
2 Установите Python и зависимости.
Настройте systemd для запуска бота:
sudo nano /etc/systemd/system/bot-assistant.service


[Unit]
Description=Telegram Bot Assistant
After=network.target

[Service]
Type=simple
ExecStart=/path/to/venv/bin/python /path/to/main.py
WorkingDirectory=/path/to/bot-assistant
Restart=always

[Install]
WantedBy=multi-user.target


Запустите

sudo systemctl enable bot-assistant
sudo systemctl start bot-assistant
```




### Author
```
Developer: Karimov Valievich Radik
```
### Adds
```
Масштабируемость: Для добавления новых полей в форму достаточно расширить класс ClientForm и обновить логику сохранения в sheet_worker.py.

Промптинг: Промпты в services/config.py позволяют легко настраивать диалог с пользователем, например, добавлять более персонализированные сообщения.

Логирование: Логи можно настроить для записи в файл или отправки в систему мониторинга (например, Sentry) через изменение logger_func.py

data folder: Папка data нужна для содержания временных или сторонних статичных файлов. На момент первой версии проекта папка эта содержит папку logs с файлом логов предупреждений разного уровня маркируя их по цвету, времени и ключевому слову уровня опасности а так же в каждом предупреждении содержится техническое маркирование ( пример: " [get_sheet_data action]: Данных нет " , где [get_sheet_data action] техническое маркирование в каком методе проходит предупреждение а после идёт само предупреждение)
Примечание - Папка data должна быть создана в корне проекта как один из элементов архитектуры (Полная первичная архитектура - main.py, пакеты - config, data, handlers, services)

config folder: Данная папка должна содержать .env файл с ключевыми данными настроек по всему проекту а так же эта папка должна быть в корне проекта.

Файл .env и его переменные: Если в файле .env, в поле DEBUG значение является True то данные из .env подтягиваются из полей тестового назначения а так же логирование производится в автоматически созданный файл test_general.log иначе в general.log


```

### Examples
```
![Пример](https://ibb.co.com/mP2Kc0w)

![Пример](https://i.postimg.cc/JnH1jYLz/photo-3-2025-04-01-09-28-41.jpg)

![Пример](https://i.postimg.cc/MHkz506b/photo-4-2025-04-01-09-28-41.jpg)

![Пример](https://i.postimg.cc/g0Jc2ktR/photo-2-2025-04-01-09-28-41.jpg)

![Пример](https://i.postimg.cc/HLhYcDFN/photo-5-2025-04-01-09-28-41.jpg)

![Пример](https://i.postimg.cc/rwgFTtjM/photo-1-2025-04-01-09-28-41.jpg)

```
>>>>>>> 6f621cb (maked test tast of ai assistant)
