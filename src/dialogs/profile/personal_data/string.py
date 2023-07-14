

passport = {
    "first_name": {
        "type": "Имя",
        "request": "Пришлите ваше - имя",
        "example": "Тимофей",
        "input": ["text"]
    },
    "surname": {
        "type": "Фамилия",
        "request": "Пришлите вашу - фамилию",
        "example": "Лазарев",
        "input": ["text"]
    },
    "middle_name": {
        "type": "Отчество",
        "request": "Пришлите ваше - отчество\nЕсли его нет пришлите в ответ 'нет'",
        "example": "Сергеевич",
        "input": ["text"]
    },
    "passport_series": {
        "type": "Серия паспорта",
        "request": "Пришлите - серию паспорта",
        "example": "1234",
        "input": ["int"]
    },
    "passport_number": {
        "type": "Номер паспорта",
        "request": "Пришлите - номер паспорта",
        "example": "567890",
        "input": ["int"]
    },
    "who_issued_it": {
        "type": "Кем выдан",
        "request": "Пришлите - кем выдан паспорт",
        "example": "ЮВ г.Москва паспортный отдел",
        "input": ["text", "space"]
    },
    "date_of_issue": {
        "type": "Дата выдачи",
        "request": "Выберете - дату выдачи паспорта",
        "example": "07.08.2010",
        "input": ["date"]
    },
    "unit_code": {
        "type": "Код региона",
        "request": "Пришлите - код региона",
        "example": "660-550",
        "input": ["int", "minus"]
    },
    "date_of_birth": {
        "type": "Дата рождения",
        "request": "Выберете - дату рождения",
        "example": "07.09.2003",
        "input": ["date"]
    },
    "place_of_birth": {
        "type": "Место рождения",
        "request": "Пришлите - место рождения",
        "example": "Москва",
        "input": ["text"]
    },
    "registration_address": {
        "type": "Адрес регистрации",
        "request": "Пришлите - адрес регистрации",
        "example": "Москва, ул.Арбат, д.13, кв.110",
        "input": ["text", "space"]
    }
}

bank = {
    "recipient": {
        "type": "Имя: ",
        "request": "Пришлите ваше - имя",
        "example": "Тимофей",
        "input": ["text"]
    },
    "account_code": {
        "type": "Фамилия: ",
        "request": "Пришлите вашу - фамилию",
        "example": "Лазарев",
        "input": ["text"]
    },
    "bik_code": {
        "type": "Отчество: ",
        "request": "Пришлите ваше - отчество\nЕсли его нет пришлите в ответ 'нет'",
        "example": "Сергеевич",
        "input": ["text"]
    },
    "bank_recipient": {
        "type": "Серия паспорта: ",
        "request": "Пришлите - серию паспорта",
        "example": "1234",
        "input": ["int"]
    },
    "correct_code": {
        "type": "Номер паспорта: ",
        "request": "Пришлите - номер паспорта",
        "example": "567890",
        "input": ["int"]
    },
    "inn_code": {
        "type": "Кем выдан: ",
        "request": "Пришлите - кем выдан паспорт",
        "example": "ЮВ г.Москва паспортный отдел",
        "input": ["text"]
    },
    "kpp_code": {
        "type": "Дата выдачи: ",
        "request": "Выберете - дату выдачи паспорта",
        "example": "07.08.2010",
        "input": ["date"]
    },
    "swift_code": {
        "type": "Код региона: ",
        "request": "Пришлите - код региона",
        "example": "660-550",
        "input": ["int", "minus"]
    }
}
