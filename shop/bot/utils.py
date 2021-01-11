import json
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup
from .constants import constants_bot


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


def init_cart_button(tags, id_field='id'):
    kb = InlineKeyboardMarkup()
    data = []
    for tag in tags:
        button = InlineKeyboardButton(
            text=constants_bot.CART_KB[tag],
            callback_data=json.dumps({
                "id": str(id_field),
                "tag": tag
            }))
        data.append(button)
    kb.row(*data)
    return kb

