from sqlalchemy import update
from sqlalchemy.future import select
from datetime import datetime, timedelta, timezone
import asyncio
from config import client, engine, SessionLocal, Base
from models.model import Status, User
from pyrogram.handlers import MessageHandler
from pyrogram.types import Message
from pyrogram import Client, filters
from sqlalchemy.future import select
import config_messages


utc_tz = timezone.utc


async def check_triggers(message: str):
    """
    Проверяет сообщение на наличие заданных триггеров.

    :param message: Строка, содержащая текст сообщения.
    :return: Возвращает True, если найден триггер, иначе False.
    """
    triggers = ['Триггер1']
    for trigger in triggers:
        try:
            if trigger in message:
                return True
        except TypeError:
            pass
    return False


async def update_user_status(session: SessionLocal, user_id: int, new_status: Status, current_time: datetime):
    """
    Обновляет статус пользователя в базе данных.

    :param session: Сессия базы данных.
    :param user_id: Идентификатор пользователя.
    :param new_status: Новый статус для установки.
    :param current_time: Текущее время обновления статуса.
    """
    stmt = (
        update(User)
        .where(User.id == user_id)
        .values(status=new_status, status_updated_at=current_time)
    )
    await session.execute(stmt)
    await session.commit()


async def delete_message(user_id: int, message_ids: list):
    '''
    Удаляет сообщения пользователя.
    '''
    try:
        await client.delete_messages(user_id, message_ids)
    except Exception as e:
        pass
    
    
async def check_stopwords(message: str, message_id, session: SessionLocal, user_id: int, current_time: datetime):
    """
    Проверяет сообщение на наличие стоп-слов и выполняет соответствующие действия.

    :param message: Текст сообщения для проверки.
    :param session: Сессия базы данных.
    :param user_id: Идентификатор пользователя.
    :param current_time: Текущее время для обновления временных меток.
    :return: Возвращает True, если найдено стоп-слово 'прекрасно', иначе False.
    """
    stopwords = {
        'прекрасно': True,
        'ожидать': 'update_date'
    }

    for word, action in stopwords.items():
        if word in message.lower():
            if action == True:
                return True
            elif action == 'update_date':
                await delete_message(user_id, [message_id])
                user = await session.execute(select(User).where(User.id == user_id))
                user = user.scalars().first()
                if user:
                    if user.msg1_sent_at is None:
                        user.created_at = current_time
                    elif user.msg2_sent_at is None:
                        user.msg1_sent_at = current_time
                    elif user.msg3_sent_at is None:
                        user.msg2_sent_at = current_time
                    await session.commit()
    return False


async def get_alive_users(session: SessionLocal):
    """
    Получает список активных пользователей из базы данных.

    :param session: Сессия базы данных для запросов.
    :return: Список активных пользователей.
    """
    result = await session.execute(select(User).where(User.status == Status.alive))
    return result.scalars().all()


async def send_message(app: Client, user_id: int, text: str):
    """
    Отправляет сообщение пользователю.

    :param app: Экземпляр клиента Pyrogram.
    :param user_id: Идентификатор пользователя.
    :param text: Текст сообщения для отправки.
    :return: Возвращает True при успешной отправке, иначе False.
    """
    try:
        await app.send_message(user_id, text)
    except Exception as e:
        print(f"Error sending message to {user_id}: {e}")
        return False
    return True


async def update_msg_sent_at(session: SessionLocal, user_id: int, msg_column: str, current_time: datetime):
    """
    Обновляет время отправки сообщения в базе данных.

    :param session: Сессия базы данных.
    :param user_id: Идентификатор пользователя.
    :param msg_column: Название столбца для обновления времени отправки.
    :param current_time: Текущее время для записи.
    """
    stmt = (
        update(User)
        .where(User.id == user_id)
        .values({msg_column: current_time})
    )
    await session.execute(stmt)
    await session.commit()


async def process_messages(app: Client, session: SessionLocal):
    """
    Обрабатывает сообщения от пользователей и выполняет действия в зависимости от условий.

    :param app: Экземпляр клиента Pyrogram.
    :param session: Сессия базы данных.
    """
    users = await get_alive_users(session)
    now = datetime.utcnow().replace(tzinfo=utc_tz)  # Убедитесь, что now имеет временную зону UTC
    for user in users:
        stopword_found = False
        async for message in app.get_chat_history(user.id, limit=10):
            if await check_stopwords(str(message.text), message.id, session, user.id, now):
                stopword_found = True
                break

        if stopword_found:
            await update_user_status(session, user.id, Status.dead, now)
            continue

        if user.msg3_sent_at:
            continue
        elif user.msg1_sent_at is None and now >= user.created_at.replace(tzinfo=utc_tz) + timedelta(minutes=6):
            if await send_message(app, user.id, "Текст1"):
                await update_msg_sent_at(session, user.id, 'msg1_sent_at', now)
        elif user.msg1_sent_at and user.msg2_sent_at is None and now >= user.msg1_sent_at.replace(tzinfo=utc_tz) + timedelta(minutes=39):
            trigger_found = False
            async for message in app.get_chat_history(user.id, limit=10):
                if await check_triggers(message.text):
                    trigger_found = True
                    break
            if not trigger_found:
                if await send_message(app, user.id, "Текст2"):
                    await update_msg_sent_at(session, user.id, 'msg2_sent_at', now)
        elif user.msg2_sent_at and user.msg3_sent_at is None and now >= user.msg2_sent_at.replace(tzinfo=utc_tz) + timedelta(days=1, hours=2):
            if await send_message(app, user.id, "Текст3"):
                await update_msg_sent_at(session, user.id, 'msg3_sent_at', now)
                await update_user_status(session, user.id, Status.finished, now)


async def main_loop():
    """
    Главный цикл программы, который создает все необходимые таблицы и обрабатывает сообщения.
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with client, SessionLocal() as session:
        while True:
            await process_messages(client, session)
            await asyncio.sleep(60)  # Check every minute


async def create_user(session: SessionLocal, user_id: int):
    """
    Создает нового пользователя в базе данных, если таковой не существует.

    :param session: Сессия базы данных.
    :param user_id: Идентификатор пользователя.
    """
    existing_user = await session.execute(select(User).where(User.id == user_id))
    existing_user = existing_user.scalar_one_or_none()
    if not existing_user:
        new_user = User(id=user_id, created_at=datetime.utcnow(), status=Status.alive, status_updated_at=datetime.utcnow())
        session.add(new_user)
        await session.commit()
        print(f"Новый пользователь добавлен: {user_id}")


@client.on_message(filters.private)
async def on_new_message(client: Client, message: Message):
    """
    Обработчик новых сообщений от пользователей.

    :param client: Экземпляр клиента Pyrogram.
    :param message: Объект сообщения Pyrogram.
    """
    user_id = message.from_user.id
    async with SessionLocal() as session:
        user = await session.execute(select(User).where(User.id == user_id))
        user = user.scalar()
        if not user:
            await create_user(session, user_id)
        else:
            print(f"Пользователь уже существует: {user_id}")


async def starting():
    """
    Инициализирует и запускает главный цикл обработки сообщений.
    """
    await asyncio.create_task(main_loop())
    await client.stop()
    
    
if __name__ == '__main__':
    client.run(starting())
