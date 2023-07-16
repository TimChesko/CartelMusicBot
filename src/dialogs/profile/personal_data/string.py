{
    "passport": {
        "first_name": {
            "type": "Имя",
            "request": "Пришлите ваше - имя",
            "example": "Тимофей",
            "input": [
                "text"
            ]
        },
        "surname": {
            "type": "Фамилия",
            "request": "Пришлите вашу - фамилию",
            "example": "Лазарев",
            "input": [
                "text"
            ]
        },
        "middle_name": {
            "type": "Отчество",
            "request": "Пришлите ваше - отчество\nЕсли его нет пришлите в ответ 'нет'",
            "example": "Сергеевич",
            "input": [
                "text"
            ]
        },
        "passport_series": {
            "type": "Серия паспорта",
            "request": "Пришлите - серию паспорта",
            "example": "1234",
            "input": [
                "int"
            ]
        },
        "passport_number": {
            "type": "Номер паспорта",
            "request": "Пришлите - номер паспорта",
            "example": "567890",
            "input": [
                "int"
            ]
        },
        "who_issued_it": {
            "type": "Кем выдан",
            "request": "Пришлите - кем выдан паспорт",
            "example": "ЮВ г.Москва паспортный отдел",
            "input": [
                "any"
            ]
        },
        "date_of_issue": {
            "type": "Дата выдачи",
            "request": "Выберете - дату выдачи паспорта",
            "example": "07.08.2010",
            "input": [
                "date"
            ]
        },
        "unit_code": {
            "type": "Код региона",
            "request": "Пришлите - код региона",
            "example": "660-550",
            "input": [
                "int",
                "minus"
            ]
        },
        "date_of_birth": {
            "type": "Дата рождения",
            "request": "Выберете - дату рождения",
            "example": "07.09.2003",
            "input": [
                "date"
            ]
        },
        "place_of_birth": {
            "type": "Место рождения",
            "request": "Пришлите - место рождения",
            "example": "Москва",
            "input": [
                "text"
            ]
        },
        "registration_address": {
            "type": "Адрес регистрации",
            "request": "Пришлите - адрес регистрации",
            "example": "Москва, ул.Арбат, д.13, кв.110",
            "input": [
                "any"
            ]
        }
    },
    "bank": {
        "recipient": {
            "type": "ФИО",
            "request": "Пришлите ваше - ФИО",
            "example": "Лазарев Тимофей Сергеевич",
            "input": [
                "text",
                "space"
            ]
        },
        "account_code": {
            "type": "Номер счета",
            "request": "Пришлите - номер счета",
            "example": "40217210300013628341",
            "input": [
                "big_int"
            ]
        },
        "bik_code": {
            "type": "БИК код",
            "request": "Пришлите - банковский идентификационный код",
            "example": "044525974",
            "input": [
                "big_int"
            ]
        },
        "bank_recipient": {
            "type": "Банк получателя",
            "request": "Пришлите - банк получателя",
            "example": "АО «Тинькофф Банк»",
            "input": [
                "any"
            ]
        },
        "correct_code": {
            "type": "Корреспондентский счет",
            "request": "Пришлите - корреспондентский счет",
            "example": "30101810145250000974",
            "input": [
                "int"
            ]
        },
        "inn_code": {
            "type": "ИНН",
            "request": "Пришлите - ИНН",
            "example": "7710341679",
            "input": [
                "big_int"
            ]
        },
        "kpp_code": {
            "type": "КПП код",
            "request": "Пришлите - код причины постановки на учет (КПП)",
            "example": "771302001",
            "input": [
                "big_int"
            ]
        }
    }
}