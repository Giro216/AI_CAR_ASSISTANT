# # Импортируем функции для работы с базой данных из SQLAlchemy
# from sqlalchemy import create_engine
# from sqlalchemy.orm import sessionmaker, declarative_base
#
# # URL подключения к базе данных SQLite
# DATABASE_URL = "sqlite:///./finance.db"
#
# # Создаем движок для подключения к базе данных
# # check_same_thread=False позволяет использовать SQLite в многопоточной среде
# engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
#
# # Создаем фабрику для создания сессий работы с базой данных
# # autocommit=False означает, что изменения нужно сохранять вручную через commit()
# # autoflush=False означает, что изменения не применяются автоматически
# SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
#
# # Базовый класс для всех моделей базы данных
# Base = declarative_base()
#
