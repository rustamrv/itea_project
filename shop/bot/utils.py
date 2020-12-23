import json
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup


def inline_kb_from_iterable(
        tag,
        iterable,
        id_field='id',
        text_field='title'
):
    buttons = []
    for i in iterable:
        json_data = json.dumps({
            id_field: str(getattr(i, id_field)),
            'tag': tag
        })
        buttons.append(
            InlineKeyboardButton(
                text=getattr(i, text_field),
                callback_data=json_data
            )
        )
    kb = InlineKeyboardMarkup()
    kb.add(*buttons)
    return kb
