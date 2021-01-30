from flask import Flask, render_template, redirect, url_for, request
from shop.api.resources import PostAddCategory, PostAddProduct, RestOrder, RestCatalog, RestProducts

from flask_restful import Api


admin = Flask(__name__, template_folder='templates')
api = Api(admin)
api.add_resource(RestProducts, '/api/products')
api.add_resource(RestCatalog, '/api/catalogs')
api.add_resource(RestOrder, '/api/orders')
api.add_resource(PostAddCategory, '/api/add_category')
api.add_resource(PostAddProduct, '/api/add_product')


