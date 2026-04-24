# # Импортируем класс Decimal для точных вычислений с деньгами
# from decimal import Decimal
# from datetime import datetime
# # Импортируем классы для работы с базой данных из SQLAlchemy
# from sqlalchemy import Column, Integer, ForeignKey
# from sqlalchemy.orm import Mapped, mapped_column
#
# # Импортируем базовый класс для моделей
# from app.database import Base
# from app.enum import CurrencyEnum
#
#
# # Модель пользователя в базе данных
# class User(Base):
#     # Название таблицы в базе данных
#     __tablename__ = "user"
#     # Уникальный идентификатор пользователя (первичный ключ)
#     id: Mapped[int] = mapped_column(primary_key=True)
#     # Логин пользователя (уникальный, обязательный для заполнения)
#     login: Mapped[str] = mapped_column(unique=True)
#
#
# # Модель кошелька в базе данных
# class Wallet(Base):
#     # Название таблицы в базе данных
#     __tablename__ = "wallet"
#
#     # Уникальный идентификатор кошелька (первичный ключ)
#     id: Mapped[int] = mapped_column(primary_key=True)
#     # Название кошелька
#     name: Mapped[str]
#     # Баланс кошелька (используем Decimal для точных вычислений)
#     balance: Mapped[Decimal]
#     # Идентификатор пользователя-владельца кошелька (внешний ключ на таблицу user)
#     user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False)
#
#     # Валюта кошелька (из перечисления CurrencyEnum)
#     currency: Mapped[CurrencyEnum]
#
#
# # Модель операции с деньгами в базе данных
# class Operation(Base):
#     # Название таблицы в базе данных
#     __tablename__ = "operation"
#
#     # Уникальный идентификатор операции (первичный ключ)
#     id: Mapped[int] = mapped_column(primary_key=True)
#     # Идентификатор кошелька, к которому относится операция (внешний ключ на таблицу wallet)
#     wallet_id: Mapped[int] = mapped_column(ForeignKey("wallet.id"))
#     # Тип операции (расход, доход или перевод)
#     type: Mapped[str]
#     # Сумма операции (используем Decimal для точных вычислений)
#     amount: Mapped[Decimal]
#     # Валюта операции (из перечисления CurrencyEnum)
#     currency: Mapped[CurrencyEnum]
#     # Категория операции (необязательное поле, по умолчанию None)
#     category: Mapped[str | None] = mapped_column(default=None)
#     # Подкатегория операции (необязательное поле, по умолчанию None)
#     subcategory: Mapped[str | None] = mapped_column(default=None)
#     # Дата и время создания операции (по умолчанию текущее время)
#     created_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now())
#