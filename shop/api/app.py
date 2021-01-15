import os

from flask import Blueprint, render_template, redirect, url_for, request
from ..models.shop_models import Category, Product, User, Order
from ..models.extra_models import News
from ..bot.config import WEBHOOK_URI

admin = Blueprint('admin', __name__)


@admin.route('/')
@admin.route('/index')
def index():
    return render_template('index.html')


@admin.route('/add_group', methods=['GET', 'POST'])
def add_group():
    if request.method == "GET":
        categories = Category.objects
        data = {
            "categories": categories,
        }
        return render_template('/add_group.html', **data)
    else:
        data_form = dict(request.form)
        category = Category()
        category.title = data_form['name']
        category.save()
        if data_form['parent']:
            category.add_subcategory(Category.objects.get(id=data_form['parent']))
        return redirect(url_for('.index'))


@admin.route('/add_product', methods=['GET', 'POST'])
def add_product():
    if request.method == "GET":
        categories = Category.objects
        data = {
            "categories": categories,
        }
        return render_template('/add_product.html', **data)
    else:
        data_form = dict(request.form)
        product = Product()
        product.title = data_form["title"]
        product.description = data_form["description"]
        product.price = float(data_form["price"])
        product.category = Category.objects.get(id=data_form['parent'])
        file = request.files['file']
        if file.filename != '':
            file.save(file.filename)
            product.image.put(file, content_type='image/png', filename=file.filename)
            os.remove(file.filename)
        product.save()
        return redirect(url_for('.products'))


@admin.route('/products', methods=['GET', 'POST'])
def products():
    if request.method == "GET":
        products = Product.objects
        data = {
            "products": products,
        }
        return render_template('list_of_products.html', **data)


@admin.route('/users')
def users():
    users = User.objects
    data = {
        "users": users,
    }
    return render_template('list_of_users.html', **data)


@admin.route('/news')
def news():
    news = News.objects
    data = {
        "news": news,
    }
    return render_template('list_of_news.html', **data)


@admin.route('/orders')
def orders():
    orders = Order.objects
    data = {
        "orders": orders,
    }
    return render_template('list_of_order.html', **data)


@admin.route('/delete/<product_id>')
def delete_product(product_id=None):
    product = Product.objects.get(id=product_id)
    product.delete()
    return redirect(url_for('.products'))


@admin.route('/edit_product/<product_id>')
def edit_product(product_id=None):
    product = Product.objects.get(id=product_id)
    # edit
    return redirect(url_for('.products'))


@admin.route('/add_news', methods=['GET', 'POST'])
def add_news():
    if request.method == "GET":
        return render_template('add_news.html')
    else:
        data_form = dict(request.form)
        news_ = News()
        news_.title = data_form["title"]
        news_.body = data_form["description"]
        news_.save()
        return redirect(url_for('.news'))
