# Telegram UserBot

Этот репозиторий содержит пример Юзер бота Telegram, созданного с помощью Pyrogram и SQLAlchemy (используются асинхронные библиотеки). Бот отслеживает сообщения пользователей и выполняет различные действия на основе заранее заданных условий.

## Функции

- Отслеживает личные сообщения по определенным ключевым словам и триггерам.
- Обновляет статус пользователя и временные метки сообщений в базе данных SQLite.
- Отправляет заранее определенные сообщения пользователям в зависимости от их активности и времени.

## Requirements

- Python 3.10+
- [Pyrogram](https://docs.pyrogram.org/)
- [SQLAlchemy](https://www.sqlalchemy.org/)
- [SQLite](https://www.sqlite.org/index.html)

## Setup

1.**Клонировать репозиторий:**
   ```sh
   git clone https://github.com/yourusername/telegram_userbot.git
   cd telegram_userbot
   ```

2. **Создайте виртуальную среду и активируйте ее:**
   ```sh
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```

3. **Install the required packages:**
   ```sh
   pip install -r requirements.txt
   ```

4. **Настройте токен и базу данных бота:**
   Создайте файл config.py и добавьте токен бота и URL-адрес базы данных:
   ```python
   # config.py
   from pyrogram import Client

   api_id = 'YOUR_API_ID'
   api_hash = 'YOUR_API_HASH'
   bot_token = 'YOUR_BOT_TOKEN'

   client = Client("my_bot", api_id=api_id, api_hash=api_hash, bot_token=bot_token)

   from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
   from sqlalchemy.orm import sessionmaker

   DATABASE_URL = "sqlite+aiosqlite:///./test.db"

   engine = create_async_engine(DATABASE_URL, echo=True)
   SessionLocal = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)
   ```

## Модели баз данных

Модели базы данных определены в `models/model.py`.Здесь `User`модель:

```python
from sqlalchemy import Column, Integer, DateTime, Enum
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime, timezone
from enum import Enum as PyEnum

Base = declarative_base()
utc_tz = timezone.utc

class Status(PyEnum):
    alive = "alive"
    dead = "dead"
    finished = "finished"

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, default=lambda: datetime.utcnow().replace(tzinfo=utc_tz))
    status = Column(Enum(Status), default=Status.alive)
    status_updated_at = Column(DateTime, default=lambda: datetime.utcnow().replace(tzinfo=utc_tz))
    msg1_sent_at = Column(DateTime, nullable=True)
    msg2_sent_at = Column(DateTime, nullable=True)
    msg3_sent_at = Column(DateTime, nullable=True)
```

## Основная логика бота

Основная логика бота реализована в файле start2.py. Вот краткий обзор основных функций:

- `check_triggers(message: str)`: проверяет, содержит ли сообщение предопределенные триггеры.
- `update_user_status(session, user_id, new_status, current_time)`: обновляет статус пользователя в базе данных.
- `check_stopwords(message: str)`: проверяет, содержит ли сообщение стоп-слова.
- `get_alive_users(session)`: извлекает активных пользователей из базы данных.
- `send_message(app, user_id, text)`: отправляет сообщение пользователю.
- `update_msg_sent_at(session, user_id, msg_column, current_time)`: обновляет метку времени отправленного сообщения в базе данных.
- `process_messages(app, session)`: обрабатывает сообщения пользователя и выполняет действия в зависимости от условий.
- `create_user(session, user_id)`: Создает нового пользователя в базе данных, если он еще не существует.
- `on_new_message(client, message)`: обработчик новых сообщений от пользователей.

## Запуск бота

Чтобы запустить бота, просто выполните скрипт start2.py:

```sh
python start2.py
```

Бот начнет отслеживать сообщения и взаимодействовать с пользователями на основе заданной логики.
