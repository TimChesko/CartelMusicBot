from aiogram.enums import ContentType

from src.utils.enums import FeatStatus

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
    text = {key: value.value if type(value) == FeatStatus else value for key, value in vars(docs).items() if is_text_key(key) and value is not None}
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


async def get_attachment_track(dialog_manager, files, track, stub_scroll_id):
    if files:
        current_page = int(await dialog_manager.find(stub_scroll_id).get_page())

        files_list = list(files.keys())
        files.update({"track_id": track.file_id_audio})
        file_types = {
            "track_id": ContentType.AUDIO,
            "text_file_id": ContentType.DOCUMENT,
            "beat_alienation": ContentType.DOCUMENT,
            "words_alienation": ContentType.DOCUMENT
        }
        file_type = file_types[files_list[current_page]]
        file_id = files[files_list[current_page]]
    else:
        file_type = ContentType.AUDIO
        file_id = track.file_id_audio
    return file_type, file_id
