from ..models.shop_models import Product, Category
from flask import request
from flask_restful import Resource
import json


class RestProducts(Resource):
    def get(self, tag_id=None):
        if tag_id:
            pass
        else:
            users = Product.objects()
            user_json = users.to_json()
            return json.loads(user_json)


class RestCatalog(Resource):
    def get(self, tag_id=None):
        if tag_id:
            pass
        else:
            users = Category.objects()
            user_json = users.to_json()
            return json.loads(user_json)
