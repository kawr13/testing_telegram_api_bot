import pytest
from start2 import check_triggers, check_stopwords

@pytest.mark.asyncio
async def test_check_triggers():
    message_with_trigger = "Это сообщение содержит слово Триггер1"
    message_without_trigger = "Это просто сообщение"
    # Проверка на наличие триггера
    assert await check_triggers(message_with_trigger) == True
    # Проверка отсутствия триггера
    assert await check_triggers(message_without_trigger) == False

@pytest.mark.asyncio
async def test_check_stopwords():
    message_with_stopword = "Это сообщение содержит слово прекрасно"
    message_without_stopword = "Это сообщение без стоп-слов"
    # Проверка на наличие стоп-слова
    assert await check_stopwords(message_with_stopword) == True
    # Проверка отсутствия стоп-слова
    assert await check_stopwords(message_without_stopword) == False