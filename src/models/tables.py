from datetime import datetime

from sqlalchemy import String, Integer, DateTime, Boolean, ForeignKey, Column, BigInteger
from sqlalchemy.orm import DeclarativeBase, relationship, column_property


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
    chats = relationship("Chats", back_populates="user")  # Добавить связь с Chats
    albums = relationship("Album", back_populates="user")

    # def __repr__(self):
    #     return f"User(tg_id='{self.tg_id}', first_name='{self.first_name}', surname='{self.surname}')"
    # now I don't know how to use it \0_0/


class PersonalData(Base):
    __tablename__ = 'personal_data'
    tg_id = Column(BigInteger, ForeignKey('users.tg_id'), primary_key=True, nullable=False)
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
    all_user_data = Column(Boolean, default=False)

    # Банковские данные
    recipient = Column(String)  # Получатель
    account_code = Column(Integer)  # Номер счёта
    bik_code = Column(Integer)  # БИК
    bank_recipient = Column(String)  # Банк получатель
    correct_code = Column(Integer)  # Корр. Счет
    inn_code = Column(Integer)  # ИНН
    kpp_code = Column(Integer)  # КПП
    swift_code = Column(String)  # Свифт-код
    all_cash_data = Column(Boolean, default=False)

    moderated = Column(Boolean, default=False)


class Track(Base):
    __tablename__ = "tracks"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey('users.tg_id'), nullable=False)  # Ссылка на таблицу users
    album_id = Column(Integer, ForeignKey('albums.id'))  # новая ссылка на альбом

    track_title = Column(String)
    file_id_audio = Column(String)
    approved = Column(Boolean, default=False)
    id_who_approve = Column(BigInteger)

    datetime = Column(DateTime, nullable=False)  # дату доставать из msg

    process = Column(Boolean, default=True)
    reject = Column(Boolean, default=False)
    approve = Column(Boolean, default=False)
    approve_promo = Column(Boolean, default=False)  # Принятие трека с доступом к промо
    aggregating = Column(Boolean, default=False)  # Трек на отгрузке агрегатору
    aggregated = Column(Boolean, default=False)  # Трек отгружен агрегатору

    # Свойство column_property для гарантии уникальности значений True
    process_only = column_property(process & ~reject & ~approve & ~approve_promo & ~aggregating & ~aggregated)
    reject_only = column_property(~process & reject & ~approve & ~approve_promo & ~aggregating & ~aggregated)
    approve_only = column_property(~process & ~reject & approve & ~approve_promo & ~aggregating & ~aggregated)
    approve_promo_only = column_property(~process & ~reject & ~approve & approve_promo & ~aggregating & ~aggregated)
    aggregating_only = column_property(~process & ~reject & ~approve & ~approve_promo & aggregating & ~aggregated)
    aggregated_only = column_property(~process & ~reject & ~approve & ~approve_promo & ~aggregating & aggregated)


    # Определение связи с TrackInfo
    track_info = relationship("TrackInfo", uselist=False, back_populates="track")
    album = relationship('Album', back_populates='tracks')  # новое отношение с альбомом


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
    user_id = Column(Integer, ForeignKey('users.tg_id'))
    album_cover = Column(String)  # Обложка

    signed_license = Column(String)  # Подписанное ЛС на проверку
    unsigned_license = Column(String)  # Неподписанное ЛС на проверку
    mail_track_photo = Column(String)  # трек номер отправленного письма с ЛС

    tracks = relationship('Track', back_populates='album')  # новое отношение с треками
    user = relationship("User", back_populates="albums")
