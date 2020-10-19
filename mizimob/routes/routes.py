from flask import render_template, request, redirect, url_for, flash
from flask_login import login_user, current_user, logout_user, login_required
from mizimob import app, bcrypt, db
from mizimob.forms.product import LoginForm, ProductForm, CategoryForm
from mizimob.models.models import User, Category, CategorySChema, UserSchema, Product, Media, MediaSchema, ProductSchema
from flask_sqlalchemy import sqlalchemy
import secrets, os
from PIL import Image

user_schema = UserSchema()
users_schema = UserSchema(many=True)

category_schema = CategorySChema()
categories_schema = CategorySChema(many=True)

product_schema = ProductSchema()
products_schema = ProductSchema(many=True)

image_schema = MediaSchema()
images_schema = MediaSchema(many=True)


@app.route('/')
def home():
    # get products from the database
    products = Product.query.all()
    product_dict = products_schema.dump(products)
    # name
    new_products = list()
    category_mapper = {"1": "events", "2": "title", "3": "rental"}
    for product in product_dict:
        index = product["category"]
        product["category"] = category_mapper[f"{index}"]
        new_products.append(product)
        try:
            lookup = Media.query.filter_by(product_id=product["id"]).first()
            image = image_schema.dump(lookup)
            file = image_schema.dump(lookup)["file"]
            product["image"] = file
        except KeyError:
            file = "default.jpg"
            product["image"] = file

        print(product)
    return render_template("index.html", products=new_products)


@app.route('/product/<string:name>')
def item(name):
    #  we are going  to get the name from the database
    # get images and file fron the database and sho them here
    lookup = Product.query.filter_by(name=name).first()
    media_lookup = Media.query.filter_by(product_id=lookup.id).all()
    category_mapper = {"1": "Events", "2": "Title", "3": "Rental"}

    # media_data
    lookup_data = product_schema.dump(lookup)
    media_data = images_schema.dump(media_lookup)
    images = list()
    for media in media_data:
        images.append(media['file'])
    lookup_data["images"] = images
    index = lookup_data["category"]
    lookup_data["category"] = category_mapper[f"{index}"]
    print(lookup_data)
    return render_template("work-single.html", product=lookup_data)


@app.route("/admin/login", methods=["POST", 'GET'])
def login():
    # login = LoginForm()
    if current_user.is_authenticated:
        return redirect(url_for("products_all"))

    # loading the form
    login = LoginForm()

    # checking the form data status
    if login.validate_on_submit():
        print("form_data", login.email.data, login.password.data)
        user = User.query.filter_by(email=login.email.data).first()
        if user and bcrypt.check_password_hash(user.password, login.password.data):
            next_page = request.args.get("next")
            login_user(user)
            return redirect(next_page) if next_page else redirect(url_for('products_all'))
        else:
            flash("Login unsuccessful Please Check Email and Password", "danger ")
    return render_template("login.html", form=login)


@app.route("/admin/product/all")
@login_required
def products_all():
    # get products from the database
    products = Product.query.all()
    product_dict = products_schema.dump(products)
    # name
    new_products = list()
    category_mapper = {"1": "events", "2": "title", "3": "rental"}
    for product in product_dict:
        index = product["category"]
        product["category"] = category_mapper[f"{index}"]
        new_products.append(product)
        try:
            lookup = Media.query.filter_by(product_id=product["id"]).first()
            image = image_schema.dump(lookup)
            file = image_schema.dump(lookup)["file"]
            product["image"] = file
        except KeyError:
            file = "default.jpg"
            product["image"] = file

    return render_template("manage_product.html",  products=new_products)


@app.route("/test")
@login_required
def test():
    return render_template("withmenu.html")


@app.route("/admin/product/edit/<string:name>")
@login_required
def edit_project(name):
    lookup = Product.query.filter_by(name=name).first()
    form = ProductForm()
    return render_template("edit.html",product=lookup,form=form)


@app.route("/admin/category/add", methods=["POST"])
def add_category():
    form = CategoryForm()
    return render_template()


@app.route('/cart')
def cart():
    return render_template("cart.html")


@app.route("/db/seed", methods=["POST"])
def seeder():
    # category seed
    category = Category("rentals")
    db.session.add(category)

    # user seed
    user = User("Denis", "Kiruku", "254719573310", "denniskiruku@gmail.com", bcrypt.generate_password_hash("1234"))
    db.session.add(user)
    try:
        #  category
        db.session.commit()
    except sqlalchemy.exc.IntegrityError:
        return {"Error!": "DB Aleardy Seeded",
                "details": {
                    "category": category_schema.dump(category), 'user': user_schema.dump(user)
                }
                }, 500

    return {"category": category_schema.dump(category), 'user': user_schema.dump(user)}, 201


@app.route("/admin/product/add", methods=['POST', "GET"])
def add():
    form = ProductForm()
    category_mapper = {"Event": 1, "Title": 2, "Rental": 3}
    if request.method == "POST":
        if form.validate_on_submit():
            title = form.title.data
            category = category_mapper[form.category.data]
            price = form.price.data
            description = form.description.data
            expires = form.expires.data
            active = True if form.active.data == "Active" else False
            # data
            #  add to the db
            lookup = Product(title, description, category, price, expires, active)
            db.session.add(lookup)
            db.session.commit()
            #
            # # product schema data
            data = product_schema.dump(lookup)
            files = form.media.data
            filenames = []
            for file in files:
                filenames.append(file.filename)
                file.save(file.filename)
                # added the database
                lookup = Media(data['id'], file.filename)
                db.session.add(lookup)
                db.session.commit()

            flash("form data submitted is valid", "success")
        else:
            form.validate()
            flash("Error with the form", "warning")
    else:
        return render_template("add.html", form=form)

    return render_template("add.html", form=form)


@app.route("/admin/product/events", methods=['POST', "GET"])
def events():
    return render_template("events.html")


@app.route("/admin/product/travel", methods=["POST", "GET"])
def travel():
    return render_template("travel.html")


@app.route("/admin/rentals/rentals", methods=["POST", "GET"])
def rentals():
    return render_template("rentals.html")

    pass
