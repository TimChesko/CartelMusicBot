import re
from datetime import datetime

from sqlalchemy import String, Integer, DateTime, Boolean, ForeignKey, Column, BigInteger, Enum
from sqlalchemy.orm import relationship, declared_attr, as_declarative


@as_declarative()
class Base:
    @classmethod
    @declared_attr
    def __tablename__(cls) -> str:
        name = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', cls.__name__)
        return re.sub('([a-z0-9])([A-Z])', r'\1_\2', name).lower()


class User(Base):
    tg_id = Column(BigInteger, primary_key=True, nullable=False)
    tg_username = Column(String)
    tg_first_name = Column(String)
    tg_last_name = Column(String)

    nickname = Column(String)

    ban = Column(Boolean, default=False)
    last_active = Column(DateTime, default=datetime.now())

    # uselist for one-to-one, one user have only one personal data
    personal_data = relationship("PersonalData", backref="user", uselist=False)

    # chats show how to realize one-to-many
    tracks = relationship("Track", back_populates="user")  # Добавить связь с Track
    albums = relationship("Album", back_populates="user")
    employee = relationship("Employee", uselist=False, back_populates='user')


class PersonalData(Base):
    tg_id = Column(BigInteger, ForeignKey(User.tg_id), primary_key=True, nullable=False)
    confirm_use_personal_data = Column(Boolean, default=False)

    # ФИО
    first_name = Column(String)
    surname = Column(String)
    middle_name = Column(String)

    # Личные данные
    passport_series = Column(String)  # серия паспорта
    passport_number = Column(String)  # номер паспорта
    who_issued_it = Column(String)  # кем выдан
    date_of_issue = Column(DateTime)  # когда выдан
    unit_code = Column(String)  # код подразделения
    date_of_birth = Column(DateTime)  # дата рождения
    place_of_birth = Column(String)  # место рождения
    registration_address = Column(String)  # адрес регистрации
    photo_id_first = Column(String)  # фотография первой страницы паспорта
    photo_id_second = Column(String)  # фотография второй страницы паспорта
    email = Column(String)  # почта
    all_passport_data = Column(Enum("process", "reject", "approve", name="passport_status"))

    # Банковские данные
    recipient = Column(String)  # Получатель
    account_code = Column(String)  # Номер счёта
    bik_code = Column(String)  # БИК
    bank_recipient = Column(String)  # Банк получатель
    correct_code = Column(String)  # Корр. Счет
    tin_self = Column(String)  # ИНН физ лица
    tin_bank = Column(String)  # Инн банка
    kpp_code = Column(String)  # КПП
    all_bank_data = Column(Enum("process", "reject", "approve", name="bank_status"))
    moderated = Column(Boolean, default=False)

    last_datetime = Column(DateTime, default=datetime.utcnow)

    social = relationship("Social", back_populates="personal_data", uselist=False)
    comments = relationship("PersonalDataComments", back_populates="personal_data", uselist=False)

    @property
    def check_comments(self):
        return len(self.comments) > 0


class PersonalDataComments(Base):
    id = Column(Integer, primary_key=True)
    tg_id = Column(BigInteger, ForeignKey(PersonalData.tg_id), nullable=False)
    column_name = Column(String, nullable=False)
    comment = Column(String, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)

    personal_data = relationship("PersonalData", back_populates="comments")


class Social(Base):
    id = Column(Integer, primary_key=True, autoincrement=True)
    personal_data_tg_id = Column(Integer, ForeignKey(PersonalData.tg_id), nullable=False)
    title = Column(String)
    link = Column(String)

    personal_data = relationship("PersonalData", back_populates="social")


class PersonalDataTemplate(Base):
    id = Column(Integer, primary_key=True)
    header_data = Column(String)
    name_data = Column(String)
    title = Column(String)
    text = Column(String)
    example = Column(String)
    input_type = Column(String)


class Album(Base):
    """
    TODO Лимитер новых альбомов (чтобы не заспамили альбомами ничего), думаю 3 альбома одновременно будет достаточно
    TODO Сделать состояния, прикреплена обложка (после чего появляется кнопка создать ЛС), проверено подписанное ЛС,
    проверен трек номер
    TODO Также сделать заполнение ПРОМО (думаю отдельной таблицей), если подтверждено с промо
    """
    # todo не забыть добавить колонки для промо

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey(User.tg_id))
    album_cover = Column(String)  # Обложка
    album_title = Column(String)  # Название

    unsigned_state = Column(Enum("process", "reject", "approve", name="unsigned_status"))
    signed_state = Column(Enum("process", "reject", "approve", name="signed_status"))
    mail_track_state = Column(Enum("process", "reject", "approve", name="mail_status"))

    checker = Column(BigInteger)

    signed_license = Column(String)  # Подписанное ЛС на проверку
    unsigned_license = Column(String)  # Неподписанное ЛС на проверку
    mail_track_photo = Column(String)  # трек номер отправленного письма с ЛС

    approver_unsigned = Column(BigInteger)
    approver_signed = Column(BigInteger)
    approver_mail = Column(BigInteger)

    create_datetime = Column(DateTime)
    sort_datetime = Column(DateTime)

    tracks = relationship('Track', back_populates='album')  # новое отношение с треками
    user = relationship("User", back_populates="albums")


class Employee(Base):
    """
        regs - the moderator has not registered yet
        works - the moderator has been registered
        fired - the moderator has been fired (уволен)
    """

    tg_id = Column(BigInteger, ForeignKey(User.tg_id), primary_key=True, nullable=False)
    first_name = Column(String)
    surname = Column(String)
    middle_name = Column(String)

    privilege = Column(Enum('manager', 'moderator', 'curator', 'admin', name='privilege_status'), default="user")
    state = Column(Enum('regs', 'works', 'fired', name='employee_status'), default='regs')
    add_date = Column(DateTime, nullable=False)
    fired_date = Column(DateTime)
    recovery_date = Column(DateTime)

    track = relationship("Track", back_populates='employee', uselist=True)
    user = relationship("User", back_populates="employee")
    track_approvement = relationship('TrackApprovement', back_populates='employee')


class Track(Base):
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey(User.tg_id), nullable=False)  # Ссылка на таблицу users
    album_id = Column(Integer, ForeignKey(Album.id))  # новая ссылка на альбом

    track_title = Column(String, nullable=False)
    file_id_audio = Column(String, nullable=False)
    checker = Column(BigInteger)
    #  if False - task is free (no one works with it), True - task was taken by someone
    id_who_approve = Column(BigInteger, ForeignKey(Employee.tg_id))

    add_datetime = Column(DateTime, nullable=False)
    sort_datetime = Column(DateTime, nullable=False)

    status = Column(Enum('process', 'reject', 'approve',
                         'approve_promo', 'aggregating',
                         'aggregated', name='track_status'), default='process')

    # Определение связи с TrackInfo
    employee = relationship("Employee", back_populates='track')
    track_info = relationship("TrackInfo", uselist=False, back_populates="track")
    album = relationship('Album', back_populates='tracks')  # новое отношение с альбомом
    user = relationship("User", back_populates="tracks")
    track_approvement = relationship('TrackApprovement', back_populates='track')


class TrackInfo(Base):
    id = Column(Integer, primary_key=True, autoincrement=True)

    track_id = Column(Integer, ForeignKey(Track.id))
    title = Column(String)

    # Text
    text_file_id = Column(String)
    words_status = Column(Boolean, default=False)
    words_alienation = Column(String)
    words_author_percent = Column(Integer)

    # Beat
    beat_status = Column(Boolean, default=False)
    beat_alienation = Column(String)
    beatmaker_percent = Column(Integer)

    # Feat
    feat_status = Column(Boolean, default=False)
    feat_tg_id = Column(String)
    feat_percent = Column(Integer)

    # Utils
    tiktok_time = Column(String)
    explicit_lyrics = Column(Boolean)

    status = Column(Enum("wait_feat", "wait_docs_feat", "process", "approve", "reject",
                         name='track_info_status'))
    comment = Column(String)

    id_who_check = Column(String)
    # Определение связи с Track
    track = relationship('Track', back_populates='track_info', uselist=False)


class ListeningTemplates(Base):
    id = Column(Integer, primary_key=True, autoincrement=True)
    type = Column(Enum('reject', 'approve', 'approve_promo', name='template_type'), nullable=False)
    name = Column(String, nullable=False)
    content = Column(String, nullable=False)

    track_approvement = relationship('TrackApprovement', back_populates='template', uselist=False)


class TrackApprovement(Base):
    id = Column(Integer, primary_key=True, autoincrement=True)
    track_id = Column(Integer, ForeignKey(Track.id), nullable=False)
    employee_id = Column(BigInteger, ForeignKey(Employee.tg_id), nullable=False)
    datetime = Column(DateTime, nullable=False)
    template_id = Column(Integer, ForeignKey(ListeningTemplates.id))
    reason = Column(String)

    track = relationship('Track', back_populates='track_approvement')
    employee = relationship('Employee', back_populates='track_approvement')
    template = relationship('ListeningTemplates', back_populates='track_approvement', uselist=False)


class CommentsTemplate(Base):
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String)
    comment = Column(String)
    is_text = Column(Boolean)
    is_img = Column(Boolean)
