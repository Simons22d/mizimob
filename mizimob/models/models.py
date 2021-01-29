from flask_login import UserMixin
from mizimob import db, ma, login_manager
from datetime import datetime


class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False, unique=True)

    def __init__(self, name):
        self.name = name


class CategorySchema(ma.Schema):
    class Meta:
        fields = ("id", "name")


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# we are going to create the model from a user class
# the user mixen adds certain fields that are required matain the use session
# it will add certain fileds to the user class tha are essential to the user login


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    firstname = db.Column(db.String(100), unique=True, nullable=False)
    lastname = db.Column(db.String(100), unique=True, nullable=False)
    phone = db.Column(db.String(100), unique=True)
    email = db.Column(db.String(48), unique=True, nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    image_file = db.Column(db.String(20), nullable=False, default="default.jpg")
    password = db.Column(db.String(60), nullable=False)

    def __repr__(self):
        return f"User (' {self.id}', '{self.email}', '{self.image_file}' )"

    def __init__(self, firstname, lastname, phone, email, password, is_admin):
        self.firstname = firstname
        self.lastname = lastname
        self.phone = phone
        self.email = email
        self.password = password


# here we are going to create a user for the


class UserSchema(ma.Schema):
    class Meta:
        fields = ("id", "firstname", "lastname", "phone", "email", "password", "is_admin")


# creating a company class
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=False)
    date_added = db.Column(db.DateTime(), default=datetime.now)
    category = db.Column(db.ForeignKey('category.id'), nullable=False)
    price = db.Column(db.Integer, nullable=False, default=10)
    expires = db.Column(db.String(100), nullable=False)
    active = db.Column(db.Integer, nullable=False, default=1)

    def __init__(self, name, description, category, price, expires, active):
        self.name = name
        self.description = description
        self.category = category
        self.price = price
        self.expires = expires
        self.active = active


class ProductSchema(ma.Schema):
    class Meta:
        fields = ("id", "name", "category", "price", "media", "expires", "date_added", "active", "description")


class Media(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.ForeignKey("product.id"), nullable=False)
    file = db.Column(db.String(250), nullable=False)

    def __init__(self, product_id, file):
        self.product_id = product_id
        self.file = file


class MediaSchema(ma.Schema):
    class Meta:
        fields = ("id", "product_id", "file")


class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.ForeignKey('product.id'), nullable=True)
    user_id = db.Column(db.ForeignKey('user.id'), nullable=True)
    when = db.Column(db.String(255), nullable=True)
    confirmed = db.Column(db.Boolean, default=False)
    unique_code = db.Column(db.String,nullable=False)
    date_added = db.Column(db.DateTime, default=datetime.now)

    def __init__(self, product_id, user_id, when,unique_code):
        self.product_id = product_id
        self.when = when
        self.user_id = user_id
        self.unique_code = unique_code


class OrderSchema(ma.Schema):
    class Meta:
        fields = ("id", "product_id", "when", "date_added", "confirmed", "unique_code")


class Cart(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.ForeignKey('product.id'), nullable=True)
    user_id = db.Column(db.ForeignKey('user.id'), nullable=False)
    when = db.Column(db.DateTime, nullable=False, default=datetime.now)
    date_added = db.Column(db.DateTime, default=datetime.now)

    def __init__(self, product_id, user_id, when):
        self.product_id = product_id
        self.user_id = user_id
        self.when = when


class CartSchema(ma.Schema):
    class Meta:
        fields = ("id", "product_id", "user_id")


class OrderGroup(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    products = db.Column(db.String(255), nullable=False)
    user_id = db.Column(db.ForeignKey('user.id'), nullable=False)
    order_number = db.Column(db.String, nullable=False, unique=True)

    def __init__(self,products,user_id,order_number):
        self.products  = products
        self.user_id = user_id
        self.order_number = order_number


class OrderGroupSchema(ma.Schema):
    class Meta:
        fields = ("id","products","user_id","order_number")
