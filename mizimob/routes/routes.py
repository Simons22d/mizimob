from flask import render_template, request, redirect, url_for, flash, send_from_directory, redirect
from flask_login import login_user, current_user, login_required, logout_user
from flask_sqlalchemy import sqlalchemy

from mizimob import app, bcrypt, db
from mizimob.forms.product import (LoginForm, ProductForm, CategoryForm, PhoneEmail, OrderForm, CategoryForm,
                                   RegisterForm, CartForm)
from mizimob.models.models import (User, Category, CategorySchema, UserSchema, Product, Media, MediaSchema,
                                   ProductSchema, Order, OrderSchema,Cart, CartSchema)
from mizimob.others.utils import validate_email, validate_phone, send_email, reset_body, crop_max_square
import os
from PIL import Image
import time

# ---------------------------------
# ------- SETTING GLOBAL VARS -----
# ---------------------------------
user_schema = UserSchema()
users_schema = UserSchema(many=True)

category_schema = CategorySchema()
categories_schema = CategorySchema(many=True)

product_schema = ProductSchema()
products_schema = ProductSchema(many=True)

image_schema = MediaSchema()
images_schema = MediaSchema(many=True)

order_schema = OrderSchema()
orders_schema = OrderSchema(many=True)

# categories = list()
categories = Category.query.all()

back_mapper = dict()
front_mapper = dict()


def mapper():
    for x in categories:
        back_mapper.update({x.name.lower().capitalize(): x.id})
        front_mapper.update({x.id: x.name.lower().capitalize()})


mapper()


# serving some images
@app.route("/img/map-9.jpg", methods=["GET"])
def map_9():
    return send_from_directory("img", filename="map-9.jpg")


@app.route("/img/displace-circle.png", methods=["GET"])
def map_10():
    return send_from_directory("img", filename="displace-circle.png")


@app.route('/')
def home():
    # get products from the database
    products = Product.query.all()
    product_dict = products_schema.dump(products)
    # name
    new_products = list()
    for product in product_dict:
        index = product["category"]
        product["category"] = front_mapper[int(index)]
        new_products.append(product)
        try:
            lookup = Media.query.filter_by(product_id=product["id"]).first()
            image = image_schema.dump(lookup)
            file = image_schema.dump(lookup)["file"]
            product["image"] = file
        except KeyError:
            file = "default.jpg"
            product["image"] = file
    return render_template("index.html", products=new_products, categories=categories)


@app.route('/product/<string:name>', methods=["GET","POST"])
def product_item(name):
    # form
    form = CartForm()
    user_email = current_user.email
    user_id = current_user.id

    #  we are going  to get the name from the database
    # get images and file fron the database and sho them here
    product = Product.query.filter_by(name=name).first()
    media_lookup = Media.query.filter_by(product_id=product.id).all()
    # media_data
    lookup_data = product_schema.dump(product)
    media_data = images_schema.dump(media_lookup)
    images = list()
    for media in media_data:
        images.append(media['file'])
    lookup_data["images"] = images
    index = lookup_data["category"]
    lookup_data["category"] = front_mapper[int(index)]

    """
         #  we need to add the actual form
        form = OrderForm()

        #  we are going  to get the name from the database
        lookup = Product.query.filter_by(name=name).first()
        media_lookup = Media.query.filter_by(product_id=lookup.id).all()
        # media_data
        lookup_data = product_schema.dump(lookup)
        media_data = images_schema.dump(media_lookup)
        images = list()
        for media in media_data:
            images.append(media['file'])

        lookup_data["images"] = images
        index = lookup_data["category"]
        lookup_data["category"] = front_mapper[int(index)]

        if request.method == "POST":
            if form.validate_on_submit():
                phone = form.phone.data
                email = form.email.data
                where = form.where.data
                when = form.when.data
                #     here we are going to send an email and also make a db entry
                if validate_phone(phone):
                    if validate_email(email):
                        try:
                            order = Order(lookup.id, where, when, email, phone)
                            db.session.add(order)
                            if db.session.commit():
                                return render_template("request_item.html", product=lookup_data, form=form, booked=True)
                            else:
                                return render_template("request_item.html", product=lookup_data, form=form, booked=True)
                            # here we are going to send an email
                            # send_email(email,f"Order for the product {lookup.name} has been successfully made.",reset_body())
                        except Exception as e:
                            flash("Order not made. Please confirm data and try again", "error")
                    else:
                        flash("email not valid", "error")
                else:
                    flash("phone number is not valid", "error")

            else:
                flash("Please make sure all information is valid", "error")
                return render_template("request_item.html", product=lookup_data, form=form, booked=False)
        else:
            return render_template("request_item.html", product=lookup_data, form=form, booked=False)
        """

    if form.validate_on_submit():
        product = Product.query.filter_by(name=name).first()
        print(product)
        lookup = Cart(product.id, user_id)
        db.session.add(lookup)
        db.session.commit()
        flash("Item Added to cart Successfully","success")
        # time.sleep(5)
        return redirect("cart")
    else:
        flash("Item Could be added to the cart","Error")


    return render_template("work-single.html", product=lookup_data, form=form)


@app.route('/cart/view/<string:name>')
@login_required
def item_view(name):
    #  we are going  to get the name from the database
    # get images and file fron the database and sho them here
    lookup = Product.query.filter_by(name=name).first()
    media_lookup = Media.query.filter_by(product_id=lookup.id).all()
    # media_data
    lookup_data = product_schema.dump(lookup)
    media_data = images_schema.dump(media_lookup)
    images = list()
    for media in media_data:
        images.append(media['file'])
    lookup_data["images"] = images
    index = lookup_data["category"]
    lookup_data["category"] = front_mapper[int(index)]

    return render_template("cart_view.html", product=lookup_data)


@app.route("/admin/login", methods=["POST", 'GET'])
def login():
    # login = LoginForm()
    if current_user.is_authenticated:
        return redirect(url_for("products_all"))
    # loading the form
    login = LoginForm()
    # checking the form data status
    if login.validate_on_submit():
        user = User.query.filter_by(email=login.email.data).first()
        if user and bcrypt.check_password_hash(user.password, login.password.data):
            next_page = request.args.get("next")
            login_user(user)
            return redirect(next_page) if next_page else redirect(url_for('products_all'))
        else:
            flash("Login unsuccessful Please Check Email and Password", "danger ")
    return render_template("login.html", form=login)


@app.route("/user/login", methods=["POST", 'GET'])
def user_login():
    if current_user.is_authenticated:
        return redirect(url_for("products_all"))
    # loading the form
    login = LoginForm()
    # checking the form data status
    if login.validate_on_submit():
        user = User.query.filter_by(email=login.email.data).first()
        if user and bcrypt.check_password_hash(user.password, login.password.data):
            next_page = request.args.get("next")
            login_user(user)
            return redirect(next_page) if next_page else redirect(url_for('products_all'))
        else:
            flash("Login unsuccessful Please Check Email and Password", "danger ")
    return render_template("login.html", form=login)


@app.route("/user/signup", methods=["POST", 'GET'])
def user_register():
    # if current_user.is_authenticated:
    #     return redirect(url_for("home"))

    # loading the form
    form = RegisterForm()
    # get the deatil  from the form
    firstname = form.firstname.data
    lastname = form.lastname.data
    email = form.email.data
    phone = form.phone.data
    password = form.password.data
    confirm_password = form.confirm_password.data
    print(firstname, lastname, phone, email, password, confirm_password)

    # checking the form data status
    if form.validate_on_submit():
        if password == confirm_password:
            # passwords match
            hashed_password = bcrypt.generate_password_hash(password)
            user = User(firstname, lastname, phone, email, hashed_password)
            db.session.add(user)
            db.session.commit()
        else:
            flash("Password do not match", "danger")
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            next_page = request.args.get("next")
            login_user(user)
            return redirect(next_page) if next_page else redirect(url_for('products_all'))
        else:
            flash("Login unsuccessful Please Check Email and Password", "danger")
    return render_template("signup.html", form=form)


@app.route("/admin/product/all")
@login_required
def products_all():
    # get products from the database
    products = Product.query.all()
    product_dict = products_schema.dump(products)
    # name
    new_products = list()
    for product in product_dict:
        index = product["category"]
        product["category"] = front_mapper[int(index)]
        new_products.append(product)
        try:
            lookup = Media.query.filter_by(product_id=product["id"]).first()
            image = image_schema.dump(lookup)
            file = image_schema.dump(lookup)["file"]
            product["image"] = file
        except KeyError:
            file = "default.jpg"
            product["image"] = file
    return render_template("manage_product.html", products=new_products, categories=categories)


@app.route("/test")
@login_required
def test():
    return render_template("withmenu.html")


@app.route("/admin/product/edit/<string:name>", methods=["POST", "GET"])
@login_required
def edit_project(name):
    lookup = Product.query.filter_by(name=name).first()
    form = ProductForm()
    if request.method == "POST":
        if form.validate_on_submit():
            lookup.name = form.title.data
            lookup.expires = form.expires.data
            lookup.price = form.price.data
            lookup.description = form.description.data
            lookup.category = int(back_mapper[form.category.data])

            lookup.active = True if form.active.data == "Active" else False
            db.session.commit()

            data = product_schema.dump(lookup)
            files = form.media.data
            filenames = []
            for file in files:
                filenames.append(file.filename)
                path = os.path.join(os.getcwd(), "mizimob", "static", "uploads", file.filename)

                # cropping the image
                file.save(path)

                im = Image.open(path)
                image = crop_max_square(im)
                image.save(path, quality=100)

                # added the database
                lookup = Media(data['id'], file.filename)
                db.session.add(lookup)
                db.session.commit()
            flash("Data Updated Sucessfully", "success")
        else:
            flash("Please Make sure all form field are valid", "warning")
    else:
        form.title.data = lookup.name
        form.expires.data = lookup.expires
        form.description.data = lookup.description
        form.active.data = lookup.active
        form.price.data = lookup.price
    return render_template("edit.html", form=form, name=name)


@app.route("/admin/category/add", methods=["POST", "GET"])
def add_category():
    form = CategoryForm()
    if request.method == "POST":
        if form.validate_on_submit():

            # getting data from the form
            name = form.name.data

            # adding to the database
            lookup = Category(name)
            db.session.add(lookup)
            db.session.commit()

            flash(f"Category {name} Added Successfully", "success")
        else:
            flash("Error! Name Might exist.", "error")

    return render_template("add_category.html", form=form)


@app.route('/cart', methods=['POST', "GET"])
@login_required
def cart():
    data = list()
    user = current_user
    data_ = Order.query.filter_by(user_id=user.id).all()
    for item in data_:
        new = list()
        id = item.product_id
        product = Product.query.get(id)
        image = Media.query.filter_by(product_id=id).first()
        new.append(item)
        new.append(product)
        new.append(image)
        data.append(new)
        print(data)
    #  orders=lookup_datarr
    return render_template("cart_posts.html", orders=data)


@app.route("/db/seed", methods=["POST"])
def seeder():
    # user seed
    user = User("Admin", "Mode", "254719573310", "denniskiruku@gmail.com", bcrypt.generate_password_hash("1234"))
    db.session.add(user)
    try:
        #  category
        db.session.commit()
    except sqlalchemy.exc.IntegrityError:
        return {"Error!": "DB Aleardy Seeded",
                "details": {
                    'user': user_schema.dump(user)
                }
                }, 500

    return {'user': user_schema.dump(user)}, 201


@app.route("/admin/product/add", methods=['POST', "GET"])
@login_required
def add():
    form = ProductForm()
    categories = Category.query.all()
    categories = categories_schema.dump(categories)
    # update_mapper
    mapper()
    if request.method == "POST":
        if form.validate_on_submit():
            title = form.title.data
            category = int(back_mapper[form.category.data])
            price = form.price.data
            description = form.description.data
            expires = form.expires.data
            active = True if form.active.data == "Active" else False
            print(title, description, category, price, expires, active)
            # data
            lookup = Product(title, description, category, price, expires, active)
            db.session.add(lookup)
            db.session.commit()

            # product schema data
            data = product_schema.dump(lookup)
            files = form.media.data
            filenames = []

            for file in files:
                filenames.append(file.filename)
                path = os.path.join(os.getcwd(), "mizimob", "static", "uploads", file.filename)
                file.save(path)

                # added the database
                lookup = Media(data['id'], file.filename)
                db.session.add(lookup)
                db.session.commit()

                # cropping the image
                im = Image.open(path)
                image = crop_max_square(im)
                image.save(path, quality=100)

            flash("form data submitted is valid", "success")
    else:
        flash("Error with the form", "warning")
    return render_template("add.html", form=form, categories=categories)


@app.route("/admin/orders/manage", methods=['POST', "GET"])
@login_required
def order():
    # getting all the orders
    orders_lookup = Order.query.all()
    orders_data = orders_schema.dump(orders_lookup)
    for order in orders_lookup:
        order_ = list()
        lookup = Product.query.get(order.product_id)
        order_.append(order)
        order_.append(lookup)

    # for item in
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

    return render_template("manage_order.html", products=new_products, orders=orders_lookup)


@app.route("/logout", methods=["POST", "GET"])
def logout():
    logout_user()
    return redirect(url_for("login"))


@app.route("/test")
def test_():
    return render_template("test.html")
