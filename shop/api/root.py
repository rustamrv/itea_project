import os
from flask import Flask, render_template, redirect, url_for, request
from shop.models.shop_models import Category, Product, User, Order
from shop.models.extra_models import News
from flask_restful import Api
from shop.api.resources import PostAddCategory, PostAddProduct, RestOrder, RestCatalog, RestProducts

app = Flask(__name__, template_folder='templates')
api = Api(app)
api.add_resource(RestProducts, '/api/products')
api.add_resource(RestCatalog, '/api/catalogs')
api.add_resource(RestOrder, '/api/orders')
api.add_resource(PostAddCategory, '/api/add_category')
api.add_resource(PostAddProduct, '/api/add_product')


@app.route('/api')
@app.route('/api/index')
def index():
    return render_template('index.html')


@app.errorhandler(404)
def page_not_found(error):
    return 'This route does not exist {} {}'.format(request.url, error), 404


@app.route('/api/add_group', methods=['GET', 'POST'])
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
            parent = Category.objects.get(id=data_form['parent'])
            category.parent = parent
            category.save()
            parent.add_subcategory(category)
            parent.save()

        return redirect(url_for('.index'))


@app.route('/api/add_product', methods=['GET', 'POST'])
def add_product():
    if request.method == "GET":
        categories = Category.objects
        data = {
            "categories": categories,
            "add": True,
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


@app.route('/api/products', methods=['GET', 'POST'])
def products():
    if request.method == "GET":
        products = Product.objects
        data = {
            "products": products,
        }
        return render_template('list_of_products.html', **data)


@app.route('/api/users')
def users():
    users = User.objects
    data = {
        "users": users,
    }
    return render_template('list_of_users.html', **data)


@app.route('/api/news')
def news():
    news = News.objects
    data = {
        "news": news,
    }
    return render_template('list_of_news.html', **data)


@app.route('/api/orders')
def orders():
    orders = Order.objects
    data = {
        "orders": orders,
    }
    return render_template('list_of_order.html', **data)


@app.route('/api/delete/<product_id>')
def delete_product(product_id=None):
    product = Product.objects.get(id=product_id)
    product.delete()
    return redirect(url_for('.products'))


@app.route('/api/edit_product/<product_id>', methods=['GET', 'POST'])
def edit_product(product_id=None):
    product = Product.objects.get(id=product_id)
    if request.method == "GET":
        categories = Category.objects
        data = {
            "categories": categories,
            "add": False,
            "product": product,
        }

        return render_template('/add_product.html', **data)
    else:
        data_form = dict(request.form)
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


@app.route('/api/add_news', methods=['GET', 'POST'])
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


