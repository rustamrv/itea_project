from shop_models import Category, Product
import mongoengine as me

me.connect('SHOP')

cat = Category()
cat.title = "Товары"
cat.save()


cat1 = Category()
cat1.title = "Телефоны"
cat1.parent = cat
cat1.save()

cat2 = Category()
cat2.title = "Iphone"
cat1.parent = cat1
cat2.save()


product = Product()
product.title = "Айфонище"
product.description = "Айфонище описание"
product.price = 25000
product.category = cat2
file = open('2.jpg', 'rb')
product.image.put(file, content_type='image/jpeg')
product.save()


product = Product()
product.title = "Айфон 12"
product.description = "Айфон 12 описание"
product.price = 25000
product.category = cat2
file = open('3.jpg', 'rb')
product.image.put(file, content_type='image/jpeg')
product.save()

product = Product()
product.title = "Айфон 6"
product.description = "Айфон 6 описание"
product.price = 12000
product.discount = 50
product.category = cat2
file = open('4.jpg', 'rb')
product.image.put(file, content_type='image/jpeg')
product.save()


product = Product()
product.title = "Айфон 8"
product.description = "Айфон 8 описание"
product.price = 7000
product.discount = 30
product.category = cat2
file = open('5.jpg', 'rb')
product.image.put(file, content_type='image/jpeg')
product.save()