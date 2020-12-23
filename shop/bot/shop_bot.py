import json
import time
from mongoengine import NotUniqueError
from telebot import TeleBot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, Message, InlineKeyboardButton, InlineKeyboardMarkup
from telebot.types import Update
from .config import TOKEN, WEBHOOK_URI
from . import constants
from ..models.shop_models import Category, User, Product, Cart
from .utils import inline_kb_from_iterable
from flask import Flask, request, abort

bot = TeleBot(TOKEN)
app = Flask(__name__)


@app.route(WEBHOOK_URI, methods=['POST'])
def handler_webhook():
    if request.headers.get('content-type') == 'application/json':
        json_string = request.get_data().decode('utf-8')
        update = Update.de_json(json_string)
        bot.process_new_updates([update])
        return ''
    abort(403)


@bot.message_handler(commands=['start'])
def handle_start(message: Message):
    try:
        User.objects.create(
            telegram_id=message.chat.id,
            username=getattr(message.from_user, 'username', None),
            first_name=getattr(message.from_user, 'first_name', None)
        )
    except NotUniqueError:
        greetings = 'Рад тебя видеть в интернет магазины'
    else:
        name = f', {message.from_user.first_name}' if getattr(message.from_user, 'first_name') else ''
        greetings = constants.GREETINGS.format(name)
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = [KeyboardButton(n) for n in constants.START_KB.values()]
    kb.add(*buttons)
    bot.send_message(message.chat.id, greetings, reply_markup=kb)


@bot.message_handler(func=lambda m: constants.START_KB[constants.CATEGORIES] == m.text)
def handler_categories(message: Message):
    root_categories = Category.get_root_categories()
    kb = inline_kb_from_iterable(constants.CATEGORY_TAG, root_categories)
    bot.send_message(message.chat.id, 'Выберите категорию', reply_markup=kb)


@bot.message_handler(func=lambda m: constants.START_KB[constants.SETTINGS] == m.text)
def handler_settings(message: Message):
    user = User.objects.get(telegram_id=message.chat.id)
    data = user.formatted_data()
    bot.send_message(user.telegram_id,
                     data)


@bot.callback_query_handler(lambda c: json.loads(c.data)['tag'] == constants.CATEGORY_TAG)
def handler_category_click(call):
    category = Category.objects.get(
        id=json.loads(call.data)['id']
    )
    if category.subcategories:
        kb = inline_kb_from_iterable(constants.CATEGORY_TAG, category.subcategories)
        bot.edit_message_text(
            category.title,
            chat_id=call.message.chat.id,
            message_id=call.message.id,
            reply_markup=kb
        )
    else:
        products = category.get_products()
        for p in products:
            kb = InlineKeyboardMarkup()
            button = InlineKeyboardButton(
                    text=constants.ADD_TO_CART,
                    callback_data=json.dumps({
                              "id": str(p.id),
                              "tag": constants.PRODUCT_TAG
                    }))
            kb.add(button)
            bot.send_photo(call.message.chat.id,
                           p.image.read(),
                           caption=p.get_description(),
                           reply_markup=kb
                           )


@bot.callback_query_handler(lambda c: json.loads(c.data)['tag'] == constants.PRODUCT_TAG)
def handler_add_to_cart(call):
    product_id = json.loads(call.data)['id']
    product = Product.objects.get(id=product_id)
    user = User.objects.get(telegram_id=call.message.chat.id)
    cart = user.get_active_cart()
    cart.add_product(product)
    bot.answer_callback_query(
        call.id,
        'Продукт добавлен в корзину'
    )
