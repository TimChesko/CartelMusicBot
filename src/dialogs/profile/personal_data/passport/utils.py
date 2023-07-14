from src.dialogs.profile.personal_data import string


async def is_numeric_with_minus(text, is_int: bool):
    if text.startswith('-') or text.endswith('-'):
        return False
    has_minus = False
    for i, char in enumerate(text):
        if char.isdigit():
            continue
        elif char == '-' and 0 < i < len(text) - 1 \
                and not has_minus and text[i - 1].isdigit() \
                and text[i + 1].isdigit():
            has_minus = True
            if is_int:
                return False
        else:
            return False
    return True


async def find_data_location(data):
    if data in string.passport:
        return "password"
    elif data in string.bank:
        return "bank"
    else:
        return ""
