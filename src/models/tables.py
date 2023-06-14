from datetime import datetime

from sqlalchemy import String, Integer, DateTime, Boolean, ForeignKey, Column
from sqlalchemy.orm import DeclarativeBase, relationship


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "user"

    tg_id = Column(Integer, primary_key=True, nullable=False)
    tg_username = Column(String)
    tg_first_name = Column(String)
    tg_last_name = Column(String)

    nickname = Column(String)

    # ФИО
    first_name = Column(String)
    surname = Column(String)
    middle_name = Column(String)

    # Личные данные
    passport_series = Column(Integer)  # серия паспорта
    passport_number = Column(Integer)  # номер паспорта
    who_issued_it = Column(String)  # кем выдан
    date_of_issue = Column(String)  # когда выдан
    unit_code = Column(Integer)  # код подразделения
    date_of_birth = Column(DateTime)  # дата рождения
    place_of_birth = Column(String)  # место рождения
    registration_address = Column(String)  # адрес регистрации

    # Банковские данные
    recipient = Column(String)  # Получатель
    account_code = Column(Integer)  # Номер счёта
    bik_code = Column(Integer)  # БИК
    bank_recipient = Column(String)  # Банк получатель
    correct_code = Column(Integer)  # Корр. Счет
    inn_code = Column(Integer)  # ИНН
    kpp_code = Column(Integer)  # КПП
    swift_code = Column(String)  # Свифт-код

    user_links = relationship("Links", back_populates="user", cascade="all, delete-orphan")

    ban = Column(Boolean, default=False)
    privilege = Column(String, default="user")
    last_active = Column(DateTime, default=datetime.now())

    def __repr__(self):
        return f"User(tg_id='{self.tg_id}', first_name='{self.first_name}', surname='{self.surname}')"


class Links(Base):
    __tablename__ = "links"

    id = Column(Integer, primary_key=True)
    title = Column(String)
    url_link = Column(String)
    user_id = Column(Integer, ForeignKey("user.tg_id"))

    user = relationship("User", back_populates="user_links")

    def __repr__(self):
        return f"Links(title='{self.title}', url_link='{self.url_link}', user_id='{self.user_id}')"
