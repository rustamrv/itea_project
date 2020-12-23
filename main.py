from shop.bot.shop_bot import bot, app
import time
from shop.bot.config import WEBHOOK_URL

bot.remove_webhook()
time.sleep(0.5)
bot.set_webhook(WEBHOOK_URL, certificate=open('webhook_cert.pem'))
app.run()
# bot.polling()