from shop.bot.send_news import SenderCategory
from shop.models.shop_models import User
from telebot.types import KeyboardButton, ReplyKeyboardMarkup

kb = ReplyKeyboardMarkup(resize_keyboard=True)
discount = KeyboardButton(text='У нас появилось новая кнопка')
kb.add(discount)
s = Sender(User.objects, text='Внимание', reply_markup=kb)
s.send_message()