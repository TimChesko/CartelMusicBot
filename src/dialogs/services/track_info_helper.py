from aiogram import Bot
from aiogram_dialog import DialogManager

template_track_info = {
    "title": "Название",
    "words_status": "Автор слов",
    "words_author_percent": "Процент автору слов",
    "beat_status": "Автор бита",
    "beatmaker_percent": "Процент автору бита",
    "feat_status": "Статус фита",
    "feat_tg_id": "Телеграм id на фите",
    "feat_percent": "Процент от фита",
    "tiktok_time": "Время трека",
    "explicit_lyrics": "Ненормативная лексика"
}


def is_file_key(key: str):
    return key in ("track_id", "text_file_id", "beat_alienation", "words_alienation")


def is_text_key(key: str):
    return key in template_track_info.keys()


async def get_struct_data(docs):
    files = {key: value for key, value in vars(docs).items() if is_file_key(key) and value is not None}
    text = {key: value for key, value in vars(docs).items() if is_text_key(key) and value is not None}
    return files, text


async def get_struct_text(text_docs):
    return "\n".join([f"{template_track_info[key]}: {value}" for key, value in text_docs.items()])


async def get_checked_text(dict_text, checks):
    text = ""
    for key in dict_text.keys():
        if key in checks:
            text += f"❌ {template_track_info[key]}: {dict_text[key]}\n"
        else:
            text += f"{template_track_info[key]}: {dict_text[key]}\n"
    return text


async def get_struct_buttons(dict_text):
    return [[template_track_info[key], key] for key in dict_text.keys()]
