from ..models.shop_models import Product, Category, Order
from flask import request
from flask_restful import Resource
import json
from .schema import AddCategorySchema, AddProductSchema
from mongoengine.errors import ValidationError, MultipleObjectsReturned, DoesNotExist


class RestProducts(Resource):
    def get(self):
        users = Product.objects()
        user_json = users.to_json()
        return json.loads(user_json)


class RestCatalog(Resource):
    def get(self):
        users = Category.objects()
        user_json = users.to_json()
        return json.loads(user_json)


class RestOrder(Resource):
    def get(self):
        orders = Order.objects()
        user_json = orders.to_json()
        return json.loads(user_json)


class PostAddCategory(Resource):

    def post(self):
        json_data = json.loads(request.data.decode('utf-8'))
        errors = AddCategorySchema().validate(json_data)
        if errors:
            return errors
        title = json_data["title"]
        try:
            category = Category.objects.create(title=title)
            try:
                parent_name = json_data['parent']
            except KeyError:
                parent_name = ''
            if parent_name:
                try:
                    parent = Category.objects.get(title=parent_name)
                    if parent:
                        category.add_subcategory(parent)
                except DoesNotExist as errors:
                    return {'errors': 'not category parent'}

            category.save()
            user_json = category.to_json()
            return json.loads(user_json)
        except ValidationError as errors:
            return errors


class PostAddProduct(Resource):

    def post(self):
        json_data = json.loads(request.data.decode('utf-8'))
        errors = AddProductSchema().validate(json_data)
        if errors:
            return errors
        title = json_data.get('title')
        try:
            product = Product()
            product.title = title
            product.description = json_data.get('description')
            discount = json_data.get('discount')
            if discount:
                product.discount = discount
            price = json_data.get('price')
            if price is None:
                return {'errors': 'not price'}
            product.price = float(price)

            category = json_data.get('category')
            if category:
                try:
                    parent = Category.objects.get(title=category)
                    if parent:
                        product.category = parent
                except DoesNotExist as errors:
                    return {'errors': 'not category'}
            product.save()
            user_json = product.to_json()
            return json.loads(user_json)
        except (ValidationError, MultipleObjectsReturned) as errors:
            return errors

