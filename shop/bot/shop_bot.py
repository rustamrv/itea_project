import json
from mongoengine import NotUniqueError
from mongoengine.errors import ValidationError
from telebot import TeleBot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, Message, InlineKeyboardButton, InlineKeyboardMarkup
from telebot.types import Update
from .config import TOKEN, WEBHOOK_URI
from .constants import constants_bot
from ..models.shop_models import Category, User, Product
from ..models.extra_models import News
from .utils import inline_kb_from_iterable, init_cart_button
from flask import Flask, request, abort
from ..api.app import admin
from .send_news import Sender
from ..api.resources import RestCatalog, RestProducts, RestOrder, PostAddCategory, PostAddProduct
from flask_restful import Api
from threading import Thread
import time

bot = TeleBot(TOKEN)
app = Flask(__name__, template_folder='templates')
app.register_blueprint(admin, url_prefix='/admin')
api = Api(app)
api.add_resource(RestProducts, '/admin/api_product')
api.add_resource(RestCatalog, '/admin/api_catalog')
api.add_resource(RestOrder, '/admin/api_order')
api.add_resource(PostAddCategory, '/admin/api_add_category')
api.add_resource(PostAddProduct, '/admin/api_add_product')


def send_msg():
    while True:
        all_news_ = News.objects
        if not len(all_news_) == 0:
            news_ = all_news_[:len(all_news_)][len(all_news_)-1]
            sender = Sender(users=User.objects, bot=bot, _msg_data=f'{news_.title}\n {news_.body}')
            sender.send_message()
        hour = 60 * 60
        day = 24 * hour
        time.sleep(day)


Thread(target=send_msg).start()


@app.route(WEBHOOK_URI, methods=['POST'])
def handler_webhook():
    if request.headers.get('content-type') == 'application/json':
        json_string = request.get_data().decode('utf-8')
        update = Update.de_json(json_string)
        bot.process_new_updates([update])
        return ''
    abort(403)


# Handler commands


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
        greetings = constants_bot.GREETINGS.format(name)
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = [KeyboardButton(n) for n in constants_bot.START_KB.values()]
    kb.add(*buttons)
    bot.send_message(message.chat.id, greetings, reply_markup=kb)


@bot.message_handler(func=lambda m: constants_bot.START_KB[constants_bot.CATEGORIES] == m.text)
def handler_categories(message: Message):
    root_categories = Category.get_root_categories()
    kb = inline_kb_from_iterable(constants_bot.CATEGORY_TAG, root_categories)
    bot.send_message(message.chat.id, 'Каталог', reply_markup=kb)


@bot.message_handler(func=lambda m: constants_bot.START_KB[constants_bot.SETTINGS] == m.text)
def handler_settings(message: Message):
    user = User.objects.get(telegram_id=message.chat.id)
    data = user.formatted_data()
    bot.send_message(user.telegram_id,
                     data)


@bot.message_handler(func=lambda m: constants_bot.START_KB[constants_bot.PRODUCTS_WITH_DISCOUNT] == m.text)
def handler_discount(message: Message):
    data = Product.objects(discount__ne=0)
    if not data:
        bot.send_message(message.chat.id,
                         "Нет товаров со скидкой")
    for p in data:
        kb = InlineKeyboardMarkup()
        button = InlineKeyboardButton(
            text=constants_bot.ADD_TO_CART,
            callback_data=json.dumps({
                "id": str(p.id),
                "tag": constants_bot.PRODUCT_TAG
            }))
        kb.add(button)
        read = p.image.read()
        if read is None:
            bot.send_message(message.chat.id,
                             p.get_description(),
                             reply_markup=kb)
        else:
            bot.send_photo(message.chat.id,
                           read,
                           caption=p.get_description(),
                           reply_markup=kb
                           )


@bot.message_handler(func=lambda m: constants_bot.START_KB[constants_bot.ORDER] == m.text)
def handler_order(message: Message):
    user = User.objects.get(telegram_id=message.chat.id)
    cart = user.get_active_cart()
    if cart:
        order = cart.get_active_order()
        if order is None:
            bot.send_message(message.chat.id,
                             "Корзина пустая"
                             )
        elif order.sum_order == 0:
            bot.send_message(message.chat.id,
                             "Корзина пустая"
                             )
        else:
            kb = ReplyKeyboardMarkup()
            but = KeyboardButton('Отправить телефон', request_contact=True)

            kb.add(but)
            bot.send_message(message.chat.id,
                             f"Заказ на сумму {order.sum_order}",
                             reply_markup=kb
                             )
    else:
        bot.send_message(message.chat.id,
                         "Корзина пустая"
                         )


@bot.message_handler(func=lambda m: constants_bot.START_KB[constants_bot.CART] == m.text)
def handler_cart(message: Message):
    user = User.objects.get(telegram_id=message.chat.id)
    cart = user.get_active_cart()
    if cart:
        if len(cart.get_products()) == 0:
            bot.send_message(message.chat.id, "Ваша корзина пуста")
        for i in cart.get_products():
            kb = init_cart_button([constants_bot.PLUS, constants_bot.MINUS], str(i["id"]))
            bot.send_message(message.chat.id,
                             i["description"],
                             reply_markup=kb
                             )
    else:
        bot.send_message(message.chat.id, "Ваша корзина пуста")


# end handler commands


@bot.message_handler(content_types=['contact'])
def contact(message):
    if message.contact is not None:
        client_id = message.chat.id
        user = User.objects.get(telegram_id=client_id)
        cart = user.get_active_cart()
        order = cart.get_active_order()
        order.phone_number = message.contact.phone_number
        order.save()
        user.phone_number = order.phone_number
        user.save()
        kb = ReplyKeyboardMarkup(resize_keyboard=True)

        buttons = [KeyboardButton(n) for n in constants_bot.START_KB.values()]
        kb.add(*buttons)
        bot.send_message(message.chat.id, "Сохранили телефон.", reply_markup=kb)
        kb = init_cart_button([constants_bot.SET_ORDER_EMAIL], str(constants_bot.SET_ORDER_EMAIL))

        bot.send_message(message.chat.id, "Введите почту", reply_markup=kb)


@bot.callback_query_handler(lambda c: json.loads(c.data)['tag'] == constants_bot.PLUS)
def handler_add_to_cart(call):
    product_id = json.loads(call.data)['id']
    product = Product.objects.get(id=product_id)
    user = User.objects.get(telegram_id=call.message.chat.id)
    cart = user.get_active_cart()
    cart.add_product(product)
    bot.answer_callback_query(
        call.id,
        'Увеличили количество на 1'
    )
    kb = init_cart_button([constants_bot.PLUS, constants_bot.MINUS], str(product_id))

    bot.edit_message_text(
        text=cart.get_detail(product),
        chat_id=call.message.chat.id,
        message_id=call.message.id,
        reply_markup=kb
    )


@bot.callback_query_handler(lambda c: json.loads(c.data)['tag'] == constants_bot.MINUS)
def handler_remove_cart(call):
    product_id = json.loads(call.data)['id']
    product = Product.objects.get(id=product_id)
    user = User.objects.get(telegram_id=call.message.chat.id)
    cart = user.get_active_cart()
    if product in cart.products:
        cart.remove_product(product)
        bot.answer_callback_query(
            call.id,
            'Уменьшили количество на 1'
        )
        kb = init_cart_button([constants_bot.PLUS, constants_bot.MINUS], str(product_id))

        bot.edit_message_text(
            text=cart.get_detail(product),
            chat_id=call.message.chat.id,
            message_id=call.message.id,
            reply_markup=kb
        )
    else:
        if cart:
            for i in cart.get_products():
                kb = init_cart_button([constants_bot.PLUS, constants_bot.MINUS], str(i["id"]))
                bot.send_message(call.message.chat.id,
                                 i["description"],
                                 reply_markup=kb
                                 )
            else:
                bot.send_message(call.message.chat.id, "Ваша корзина пуста")
        else:
            bot.send_message(call.message.chat.id, "Ваша корзина пуста")


@bot.callback_query_handler(lambda c: json.loads(c.data)['tag'] == constants_bot.SET_ORDER_EMAIL)
def handler_order_email(call):
    constants_bot.client_status[call.message.chat.id] = constants_bot.SET_ORDER_EMAIL
    bot.edit_message_text("Введите почту",
                          chat_id=call.message.chat.id,
                          message_id=call.message.id,
                          )


@bot.callback_query_handler(lambda c: json.loads(c.data)['tag'] == constants_bot.SET_ORDER_ADDRESS)
def handler_order_address(call):
    constants_bot.client_status[call.message.chat.id] = constants_bot.SET_ORDER_ADDRESS
    bot.edit_message_text("Введите адрес доставки",
                          chat_id=call.message.chat.id,
                          message_id=call.message.id,
                          )


@bot.callback_query_handler(lambda c: json.loads(c.data)['tag'] == constants_bot.CATEGORY_TAG)
def handler_category_click(call):
    category = Category.objects.get(
        id=json.loads(call.data)['id']
    )
    if category.subcategories:
        kb = inline_kb_from_iterable(constants_bot.CATEGORY_TAG, category.subcategories)
        bot.edit_message_text(
            category.title,
            chat_id=call.message.chat.id,
            message_id=call.message.id,
            reply_markup=kb
        )
    else:
        products = category.get_products()
        if not products:
            root_categories = Category.get_root_categories()
            kb = inline_kb_from_iterable(constants_bot.CATEGORY_TAG, root_categories)
            bot.send_message(call.message.chat.id, 'Отсутсвует товары. Каталог', reply_markup=kb)
            return
        constants_bot.product_data = products
        constants_bot.ID_PRODUCT = 1
        len_product = len(products)

        for p in products[:1]:
            kb = InlineKeyboardMarkup()
            button = InlineKeyboardButton(
                text=constants_bot.ADD_TO_CART,
                callback_data=json.dumps({
                    "id": str(p.id),
                    "tag": constants_bot.PRODUCT_TAG
                }))

            kb.add(button)
            right_btn = InlineKeyboardButton(
                text=constants_bot.CART_KB[constants_bot.RIGHT],
                callback_data=json.dumps({
                    "id": str(p.id),
                    "tag": constants_bot.RIGHT
                }))
            if len_product > 1:
                kb.add(right_btn)
            read = p.image.read()
            if read is None:
                bot.send_message(call.message.chat.id,
                                 p.get_description(),
                                 reply_markup=kb)
            else:
                bot.send_photo(call.message.chat.id,
                               read,
                               caption=p.get_description(),
                               reply_markup=kb
                               )


@bot.callback_query_handler(lambda c: json.loads(c.data)['tag'] == constants_bot.RIGHT)
def handler_menu_product_right(call):
    products = constants_bot.product_data
    id_ = constants_bot.ID_PRODUCT
    step_ = id_ + 1
    constants_bot.ID_PRODUCT = step_
    len_product = len(products)
    p = products[id_: step_][0]
    kb = InlineKeyboardMarkup()
    button = InlineKeyboardButton(
        text=constants_bot.ADD_TO_CART,
        callback_data=json.dumps({
            "id": str(p.id),
            "tag": constants_bot.PRODUCT_TAG
        }))

    kb.add(button)
    if step_ == len_product:
        left_btn = InlineKeyboardButton(
            text=constants_bot.CART_KB[constants_bot.LEFT],
            callback_data=json.dumps({
                "id": str(p.id),
                "tag": constants_bot.LEFT
            }))

        kb.add(left_btn)
    else:
        right_btn = InlineKeyboardButton(
            text=constants_bot.CART_KB[constants_bot.RIGHT],
            callback_data=json.dumps({
                "id": str(p.id),
                "tag": constants_bot.RIGHT
            }))

        left_btn = InlineKeyboardButton(
            text=constants_bot.CART_KB[constants_bot.LEFT],
            callback_data=json.dumps({
                "id": str(p.id),
                "tag": constants_bot.LEFT
            }))

        kb.add(left_btn, right_btn)

    read = p.image.read()
    if read is None:
        bot.edit_message_text(
            text=p.get_description(),
            chat_id=call.message.chat.id,
            message_id=call.message.id,
            reply_markup=kb
        )
    else:
        bot.send_photo(call.message.chat.id,
                       read,
                       caption=p.get_description(),
                       reply_markup=kb
                       )


@bot.callback_query_handler(lambda c: json.loads(c.data)['tag'] == constants_bot.LEFT)
def handler_menu_product_right(call):
    products = constants_bot.product_data
    id_ = constants_bot.ID_PRODUCT
    step_ = id_ - 1
    constants_bot.ID_PRODUCT = step_
    p = products[step_: id_][0]
    kb = InlineKeyboardMarkup()
    button = InlineKeyboardButton(
        text=constants_bot.ADD_TO_CART,
        callback_data=json.dumps({
            "id": str(p.id),
            "tag": constants_bot.PRODUCT_TAG
        }))

    kb.add(button)
    if step_ == 0:
        right_btn = InlineKeyboardButton(
            text=constants_bot.CART_KB[constants_bot.RIGHT],
            callback_data=json.dumps({
                "id": str(p.id),
                "tag": constants_bot.RIGHT
            }))

        kb.add(right_btn)
    else:
        right_btn = InlineKeyboardButton(
            text=constants_bot.CART_KB[constants_bot.RIGHT],
            callback_data=json.dumps({
                "id": str(p.id),
                "tag": constants_bot.RIGHT
            }))

        left_btn = InlineKeyboardButton(
            text=constants_bot.CART_KB[constants_bot.LEFT],
            callback_data=json.dumps({
                "id": str(p.id),
                "tag": constants_bot.LEFT
            }))

        kb.add(left_btn, right_btn)

    read = p.image.read()
    if read is None:
        bot.edit_message_text(
            text=p.get_description(),
            chat_id=call.message.chat.id,
            message_id=call.message.id,
            reply_markup=kb
        )
    else:
        bot.send_photo(call.message.chat.id,
                       read,
                       caption=p.get_description(),
                       reply_markup=kb
                       )


@bot.callback_query_handler(lambda c: json.loads(c.data)['tag'] == constants_bot.NEWS)
def handler_news(call):
    all_news_ = News.objects
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = [KeyboardButton(n) for n in constants_bot.START_KB.values()]
    kb.add(*buttons)
    if not len(all_news_) == 0:
        news_ = all_news_[:len(all_news_)][len(all_news_) - 1]
        bot.send_message(call.message.chat.id, f'{news_.title}\n {news_.body}', reply_markup=kb)
    else:
        bot.send_message(call.message.chat.id, "Новостей нет", reply_markup=kb)


@bot.callback_query_handler(lambda c: json.loads(c.data)['tag'] == constants_bot.PRODUCT_TAG)
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


@bot.message_handler(content_types=["text"])
def handle_text(message):
    client_id = message.chat.id
    if client_id in constants_bot.client_status:
        if constants_bot.client_status[client_id] == constants_bot.SET_ORDER_EMAIL:
            user = User.objects.get(telegram_id=client_id)
            try:
                cart = user.get_active_cart()
                order = cart.get_active_order()
                order.email = message.text
                order.save()
                user.email = order.email
                user.save()
                kb = init_cart_button([constants_bot.SET_ORDER_ADDRESS], str(constants_bot.SET_ORDER_ADDRESS))
                constants_bot.client_status[client_id] = constants_bot.SET_ORDER_ADDRESS
                bot.send_message(message.chat.id, "Почту записали. Введите адрес доставки", reply_markup=kb)
            except ValidationError:
                bot.send_message(message.chat.id, "Не верная почту. Введите почту снова")

        elif constants_bot.client_status[client_id] == constants_bot.SET_ORDER_ADDRESS:
            user = User.objects.get(telegram_id=client_id)
            cart = user.get_active_cart()
            cart.is_active = False
            cart.save()
            order = cart.get_active_order()
            order.address = message.text
            order.save()
            constants_bot.client_status[client_id] = None
            bot.send_message(message.chat.id, "Заказ оформлен. Мы вам наберем.")
