GREETINGS = 'Привет {}. Рады тебя приветствовать в нашем магазине-боте'
ADD_TO_CART = 'Добавить в корзину'

CATEGORIES = 1
CART = 2
SETTINGS = 3
NEWS = 4
PRODUCTS_WITH_DISCOUNT = 5
ORDER = 6

START_KB = {
    CATEGORIES: 'Категории',
    CART: 'Корзина',
    SETTINGS: 'Настройки',
    NEWS: 'Новости',
    PRODUCTS_WITH_DISCOUNT: 'Продукты со скидкой',
    ORDER: 'Оформить заказ'
}

CATEGORY_TAG = 7
PRODUCT_TAG = 8
PLUS = 1
MINUS = 2
SET_ORDER_PHONE = 3
SET_ORDER_EMAIL = 4
SET_ORDER_ADDRESS = 5
LEFT = 9
RIGHT = 10

CART_KB = {
    PLUS: '+',
    MINUS: '-',
    SET_ORDER_PHONE: 'Введите телефон',
    SET_ORDER_EMAIL: 'Введите почту',
    SET_ORDER_ADDRESS: 'Введите адрес',
    LEFT: '<<',
    RIGHT: '>>'
}

client_status = {}
ID_PRODUCT = 0
product_data = None
