from datetime import datetime

from aiogram.loggers import event
from sqlalchemy import String, Integer, DateTime, Boolean, ForeignKey, Column, BigInteger, Enum
from sqlalchemy.orm import DeclarativeBase, relationship


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    tg_id = Column(BigInteger, primary_key=True, nullable=False)
    tg_username = Column(String)
    tg_first_name = Column(String)
    tg_last_name = Column(String)

    nickname = Column(String)

    ban = Column(Boolean, default=False)
    privilege = Column(String, default="user")
    last_active = Column(DateTime, default=datetime.now())

    # uselist for one-to-one, one user have only one personal data
    personal_data = relationship("PersonalData", uselist=False, back_populates="user")
    # chats show how to realize one-to-many
    tracks = relationship("Track", back_populates="user")  # Добавить связь с Track
    albums = relationship("Album", back_populates="user")


class PersonalData(Base):
    __tablename__ = 'personal_data'
    tg_id = Column(BigInteger, ForeignKey('users.tg_id'), primary_key=True, nullable=False)
    confirm_use_personal_data = Column(Boolean, default=False)

    # ФИО
    first_name = Column(String)
    surname = Column(String)
    middle_name = Column(String)

    # Личные данные
    passport_series = Column(Integer)  # серия паспорта
    passport_number = Column(Integer)  # номер паспорта
    who_issued_it = Column(String)  # кем выдан
    date_of_issue = Column(DateTime)  # когда выдан
    unit_code = Column(String)  # код подразделения
    date_of_birth = Column(DateTime)  # дата рождения
    place_of_birth = Column(String)  # место рождения
    registration_address = Column(String)  # адрес регистрации
    all_passport_data = Column(Integer, default=0)  # 0 - нет, 1 - в обработке, 2 - отклонены, 3 - проверены

    # Банковские данные
    recipient = Column(String)  # Получатель
    account_code = Column(BigInteger)  # Номер счёта
    bik_code = Column(BigInteger)  # БИК
    bank_recipient = Column(String)  # Банк получатель
    correct_code = Column(BigInteger)  # Корр. Счет
    inn_code = Column(BigInteger)  # ИНН
    kpp_code = Column(BigInteger)  # КПП
    all_bank_data = Column(Integer, default=0)  # 0 - нет, 1 - в обработке, 2 - отклонены, 3 - проверены

    social = relationship("Social", back_populates="personal_data", uselist=False)

    moderated = Column(Boolean, default=False)
    user = relationship("User", back_populates="personal_data")


class Social(Base):
    __tablename__ = 'social'

    id = Column(Integer, primary_key=True, autoincrement=True)
    personal_data_tg_id = Column(Integer, ForeignKey('personal_data.tg_id'), nullable=False)
    title = Column(String)
    link = Column(String)

    personal_data = relationship("PersonalData", back_populates="social")


class Track(Base):
    __tablename__ = "tracks"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey('users.tg_id'), nullable=False)  # Ссылка на таблицу users
    listening_chat_id = Column(BigInteger)
    album_id = Column(Integer, ForeignKey('albums.id'))  # новая ссылка на альбом

    track_title = Column(String)
    file_id_audio = Column(String)
    task_msg_id = Column(Integer)
    id_who_approve = Column(BigInteger)
    reject_reason = Column(String)

    datetime = Column(DateTime, nullable=False)  # дату доставать из msg

    status = Column(Enum('process', 'reject', 'approve',
                         'approve_promo', 'aggregating',
                         'aggregated', name='track_status'), default='process')

    # Определение связи с TrackInfo
    track_info = relationship("TrackInfo", uselist=False, back_populates="track")
    album = relationship('Album', back_populates='tracks')  # новое отношение с альбомом
    user = relationship("User", back_populates="tracks")


class TrackInfo(Base):
    __tablename__ = 'tracks_info'

    id = Column(Integer, primary_key=True, autoincrement=True)

    track_id = Column(Integer, ForeignKey('tracks.id'))  # Ссылка на таблицу tracks
    title = Column(String)
    text_file_id = Column(String)
    tiktok_time = Column(String)
    explicit_lyrics = Column(Boolean)

    beat_alienation = Column(String)  # Отчуждение на бит
    words_alienation = Column(String)  # Отчуждение на слова

    beatmaker_percent = Column(Integer)
    words_author_percent = Column(Integer)
    feat_percent = Column(Integer)

    # if False - artist author of beat/words and without feat
    beat_status = Column(Boolean, default=False)
    words_status = Column(Boolean, default=False)
    feat_status = Column(Boolean, default=False)

    # Определение связи с Track
    track = relationship('Track', back_populates='track_info', uselist=False)


class Album(Base):
    __tablename__ = 'albums'

    # todo не забыть добавить колонки для промо

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey('users.tg_id'))
    album_cover = Column(String)  # Обложка

    signed_license = Column(String)  # Подписанное ЛС на проверку
    unsigned_license = Column(String)  # Неподписанное ЛС на проверку
    mail_track_photo = Column(String)  # трек номер отправленного письма с ЛС

    tracks = relationship('Track', back_populates='album')  # новое отношение с треками
    user = relationship("User", back_populates="albums")


# class Employee(Base):
#     __tablename__ = 'employees'
#
#     id = Column(Integer, primary_key=True, autoincrement=True)
#     user_id = Column(BigInteger, ForeignKey('users.tg_id'))
#
#     first_name = Column(String)
#     surname = Column(String)
#     middle_name = Column(String)
