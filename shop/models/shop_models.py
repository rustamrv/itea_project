import mongoengine as me
import datetime


class User(me.Document):
    telegram_id = me.IntField(primary_key=True)
    username = me.StringField(min_length=2, max_lenght=128)
    first_name = me.StringField(min_length=2, max_lenght=128)
    phone_number = me.StringField(max_length=13)
    email = me.EmailField()
    is_blocked = me.BooleanField(default=True)

    def get_active_cart(self):
        cart = Cart.objects(user=self, is_active=True).first()
        if not cart:
            cart = Cart.objects.create(
                user=self
            )
        return cart

    def formatted_data(self):
        return f'Id - {self.telegram_id}\n Никнейм - {self.username}\n Имя - {self.first_name}' \
               f'\nEmail - {self.email}\n Номер телефона - {self.phone_number}'


class Category(me.Document):
    title = me.StringField(required=True)
    description = me.StringField(min_length=512)
    parent = me.ReferenceField('self')
    subcategories = me.ListField(me.ReferenceField('self'))

    def get_products(self):
        return Product.objects(category=self)

    @classmethod
    def get_root_categories(cls):
        return cls.objects(
            parent=None
        )

    def is_root(self):
        return not bool(self.parent)

    def add_subcategory(self, category):
        category.parent = self
        category.save()
        self.subcategories.append(category)
        self.save()


class Parameters(me.EmbeddedDocument):
    height = me.FloatField()
    width = me.FloatField()
    weight = me.FloatField()
    additional_description = me.StringField()


class Product(me.Document):
    title = me.StringField(required=True, max_length=256)
    description = me.StringField(max_length=500)
    in_stock = me.BooleanField(default=True)
    discount = me.IntField(min_value=0, max_value=100, default=0)
    price = me.FloatField(required=True)
    image = me.ImageField()
    category = me.ReferenceField(Category, required=True)
    parameters = me.EmbeddedDocumentField(Parameters)

    def get_description(self):
        if self.description:
            return f'{self.title}\n{self.description}\n{self.price}'
        else:
            return f'{self.title}\n{self.price}'

    @property
    def product_price(self):
        return (100 - self.discount) / 100 * self.price


class Cart(me.Document):
    user = me.ReferenceField(User, required=True)
    products = me.ListField(me.ReferenceField(Product))
    is_active = me.BooleanField(default=True)
    created_at = me.DateField()

    def save(self, *args, **kwargs):
        self.created_at = datetime.datetime.now()
        super().save(*args, **kwargs)

    def add_product(self, product):
        self.products.append(product)
        self.save()

    def remove_product(self, product):
        self.products.remove(product)
        self.save()

    def get_products(self):
        data = []

        for i in set(self.products):
            product = {
                'id': i.id,
                'description': self.get_detail(i)
            }
            data.append(product)
        return data

    def get_cost_cart(self):
        len_obj = [j.price for j in self.products]

        if len_obj:
            return sum(len_obj)
        return 0

    def get_active_order(self):
        order = Order.objects(user=self.user, cart=self).first()
        if not order or order.sum_order == 0:
            order = Order()
            order.user = self.user
            order.cart = self
            order.sum_order = self.get_cost_cart()
            if not order.sum_order == 0:
                order.save()
            else:
                return None
        return order

    def get_detail(self, product):
        len_obj = [j for j in self.products if j == product]
        return f'{product.title} \nprice {product.price} x {len(len_obj)} = {len(len_obj) * product.price}'


class Order(me.Document):
    user = me.ReferenceField(User)
    cart = me.ReferenceField(Cart)
    phone_number = me.StringField(max_length=13)
    email = me.EmailField()
    address = me.StringField()
    sum_order = me.FloatField(required=True)
    created_at = me.DateField()

    def save(self, *args, **kwargs):
        self.created_at = datetime.datetime.now()
        super().save(*args, **kwargs)
