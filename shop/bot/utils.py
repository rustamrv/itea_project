import json
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton


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
        text = getattr(i, text_field)
        buttons.append(
            InlineKeyboardButton(
                text=text,
                callback_data=json_data
            )
        )

    kb = InlineKeyboardMarkup()
    kb.add(*buttons)
    return kb


def init_cart_button(tags, id_field='id') -> object:
    kb = InlineKeyboardMarkup()
    data = []
    for tag in tags:
        json_data = json.dumps({
            'id': str(id_field),
            'tag': tag
        }, ensure_ascii=False)
        button = InlineKeyboardButton(
            text=tag,
            callback_data=json_data)
        data.append(button)
    kb.row(*data)
    return kb


def init_keyboard_request_contact(title):
    kb = ReplyKeyboardMarkup()
    but = KeyboardButton(title, request_contact=True)

    kb.add(but)
    return kb


def inline_kb_from_iterable_keyboard(iterable):
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = [KeyboardButton(n) for n in iterable]
    kb.add(*buttons)
    return kb
