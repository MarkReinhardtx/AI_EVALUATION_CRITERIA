# Встроенный модуль Python для работы
# с переменными окружения
import os
# Функция для загрузки переменных из файла .env
from dotenv import load_dotenv
# Функция для создания подключения к базе данных
from sqlalchemy import create_engine
# Инструменты SQLAlchemy для сессий и описания таблиц
from sqlalchemy.orm import DeclarativeBase, sessionmaker, Mapped, mapped_column

# Загружаем переменные из файла .env
load_dotenv()

# Получаем значение DATABASE_URL из файла .env
#
# Например:
# postgresql+psycopg://postgres:password@localhost:5432/ai_chat
DATABASE_URL = os.getenv("DATABASE_URL")

# Проверяем, удалось ли найти DATABASE_URL
if DATABASE_URL is None:
    # Если переменной нет, останавливаем приложение
    # и показываем понятную ошибку
    raise RuntimeError("В файле .env отсутствует DATABASE_URL")

# Создаём engine — объект, который знает,
# как подключаться к PostgreSQL
#
# Сам engine пока ничего не записывает
# и не создаёт таблицы
engine = create_engine(DATABASE_URL)

# Создаём фабрику сессий
#
# Через сессии приложение будет:
# - получать данные;
# - добавлять данные;
# - изменять данные;
# - удалять данные.
SessionLocal = sessionmaker(
# Все созданные сессии используют наше подключение engine
    bind=engine,
# Не отправлять изменения в базу автоматически перед выполнением каждого запроса
    autoflush=False,
# Не сохранять изменения автоматически Для сохранения нужно вызвать db.commit()
    autocommit=False,
)
# Создаём базовый класс для моделей таблиц
#
# Сам Base не является таблицей.
# От него будут наследоваться классы таблиц.
class Base(DeclarativeBase):
    pass
