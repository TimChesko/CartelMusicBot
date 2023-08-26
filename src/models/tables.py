import re
from datetime import datetime

from sqlalchemy import String, Integer, DateTime, Boolean, ForeignKey, Column, BigInteger, Enum, MetaData
from sqlalchemy.orm import relationship, declared_attr, as_declarative

from src.utils.enums import Tables, Actions, Privileges, FeatStatus, Status, EmployeeStatus


@as_declarative()
class Base:
    metadata = MetaData()

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
    last_active = Column(DateTime, default=datetime.utcnow())

    # uselist for one-to-one, one user have only one personal data
    personal_data = relationship("PersonalData", backref="user", uselist=False)

    # chats show how to realize one-to-many
    tracks = relationship("Track", back_populates="user")  # Добавить связь с Track
    release = relationship("Release", back_populates="user")


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
    all_passport_data = Column(Enum(Status, name="passport_status"))

    # Банковские данные
    recipient = Column(String)  # Получатель
    account_code = Column(String)  # Номер счёта
    bik_code = Column(String)  # БИК
    bank_recipient = Column(String)  # Банк получатель
    correct_code = Column(String)  # Корр. Счет
    tin_self = Column(String)  # ИНН физ лица
    tin_bank = Column(String)  # Инн банка
    kpp_code = Column(String)  # КПП
    all_bank_data = Column(Enum(Status, name="bank_status"))

    last_datetime = Column(DateTime, default=datetime.utcnow)
    checker_id = Column(BigInteger)

    social = relationship("Social", back_populates="personal_data", uselist=False)


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


class Release(Base):
    """
    TODO Лимитер новых альбомов (чтобы не заспамили альбомами ничего), думаю 3 альбома одновременно будет достаточно
    TODO Сделать состояния, прикреплена обложка (после чего появляется кнопка создать ЛС), проверено подписанное ЛС,
    проверен трек номер
    TODO Также сделать заполнение ПРОМО (думаю отдельной таблицей), если подтверждено с промо
    """
    # todo не забыть добавить колонки для промо

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey(User.tg_id))
    release_cover = Column(String)  # Обложка
    release_title = Column(String)  # Название

    signed_license = Column(String)  # Подписанное ЛС на проверку
    unsigned_license = Column(String)  # Неподписанное ЛС на проверку
    mail_track_photo = Column(String)  # трек номер отправленного письма с ЛС

    unsigned_status = Column(Enum(Status, name="unsigned_status"))
    signed_status = Column(Enum(Status, name="signed_status"))
    mail_track_status = Column(Enum(Status, name="mail_status"))

    date_last_edit = Column(DateTime, default=datetime.utcnow, nullable=False)
    checker_id = Column(BigInteger)

    tracks = relationship('Track', back_populates='release')  # новое отношение с треками
    user = relationship("User", back_populates="release")


class Employee(Base):
    tg_id = Column(BigInteger, primary_key=True, nullable=False)
    tg_username = Column(String)
    tg_first_name = Column(String)
    tg_last_name = Column(String)
    fullname = Column(String)

    privilege = Column(Enum(Privileges, name='privilege_status'))
    state = Column(Enum(EmployeeStatus, name='employee_status'), default=EmployeeStatus.REGISTRATION)
    add_date = Column(DateTime, nullable=False)
    fired_date = Column(DateTime)
    recovery_date = Column(DateTime)

    last_active = Column(DateTime, default=datetime.utcnow())


class Track(Base):
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey(User.tg_id), nullable=False)  # Ссылка на таблицу users
    release_id = Column(Integer, ForeignKey(Release.id))  # новая ссылка на альбом

    track_title = Column(String, nullable=False)
    file_id_audio = Column(String, nullable=False)

    date_last_edit = Column(DateTime, default=datetime.utcnow, nullable=False)
    checker_id = Column(BigInteger)  # Кто проверяет сейчас

    status = Column(Enum(Status, name='track_status'), default=Status.PROCESS)

    # Определение связи с TrackInfo
    track_info = relationship("TrackInfo", uselist=False, back_populates="track")
    release = relationship('Release', back_populates='tracks')  # новое отношение с альбомом
    user = relationship("User", back_populates="tracks")


class TrackInfo(Base):
    id = Column(Integer, primary_key=True, autoincrement=True)

    track_id = Column(Integer, ForeignKey(Track.id))
    title = Column(String)

    # Text
    text_file_id = Column(String)
    words_status = Column(Boolean, default=False)
    words_alienation = Column(String)
    words_author_fullname = Column(String)

    # Beat
    beat_status = Column(Boolean, default=False)
    beat_alienation = Column(String)
    beatmaker_fullname = Column(String)

    # Feat
    is_feat = Column(Boolean, default=False)
    feat_tg_id = Column(BigInteger)
    feat_percent = Column(Integer)

    # Utils
    tiktok_time = Column(String)
    explicit_lyrics = Column(Boolean)

    feat_status = Column(Enum(FeatStatus, name="track_info_feat_status"))
    status = Column(Enum(Status, name='status'))

    date_last_edit = Column(DateTime, default=datetime.utcnow, nullable=False)
    checker_id = Column(BigInteger)

    track = relationship('Track', back_populates='track_info', uselist=False)


class ApprovalTemplates(Base):
    id = Column(Integer, primary_key=True, autoincrement=True)
    table = Column(Enum(Tables, name='templates_table_names'), nullable=False)
    action = Column(Enum(Actions, name='action_names'), nullable=False)
    type = Column(Enum(Status, name='template_type'), nullable=False)
    title = Column(String, nullable=False)
    content = Column(String, nullable=False)


class LogsEmployee(Base):
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    employee_id = Column(BigInteger, ForeignKey(Employee.tg_id))
    table = Column(Enum(Tables, name='emp_logs_table_names'), nullable=False)
    row_id = Column(BigInteger, nullable=False)
    column_name = Column(Enum(Actions, name='column_name'), nullable=False)
    action_type = Column(Enum(Status, name='action_type'), nullable=False)
    comment = Column(String)
    datetime = Column(DateTime, default=datetime.utcnow, nullable=False)


class LogsUser(Base):
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    user_id = Column(BigInteger, ForeignKey(User.tg_id))
    table = Column(Enum(Tables, name='emp_logs_table_names'), nullable=False)
    row_id = Column(BigInteger, nullable=False)
    column_name = Column(Enum(Actions, name='column_name'), nullable=False)
    action_type = Column(Enum(Status, name='action_type'), nullable=False)
    datetime = Column(DateTime, default=datetime.utcnow, nullable=False)