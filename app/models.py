from app import db, login_manager, app
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from itsdangerous import TimedJSONWebSignatureSerializer as serializer


association_table = db.Table('association',
                             db.Column('products', db.Integer,
                                       db.ForeignKey('products.id')),
                             db.Column('orders', db.Integer,
                                       db.ForeignKey('orders.id'))
                             )


class Users(UserMixin, db.Model):

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    firstname = db.Column(db.String(24), index=True)
    lastname = db.Column(db.String(24), index=True)
    email = db.Column(db.String(50), index=True, unique=True)
    password_hash = db.Column(db.String)
    phonenumber = db.Column(db.String(18), index=True, unique=True)
    is_admin = db.Column(db.Boolean, default=False)
    # user and order relationship is a one to many
    order = db.relationship("Orders", backref='ordered_products')

    # user and kart is one to one relationship
    kart = db.relationship('Kart', uselist=False, backref='user_kart')
    # one to many relationships with Shipping info
    # change role
    shipping_info = db.relationship(
        'ShippingInfo', backref='shipping', lazy='dynamic')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_reset_token(self, expires_secs=600):
        s = serializer(app.config['SECRET_KEY'], expires_secs)
        return s.dumps({'user_id': self.id}).decode('utf-8')

    @staticmethod
    def verify_reset_token(token):
        s = serializer(app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token)['user_id']
        except:
            return None
        return Users.query.get(user_id)

    def __repr__(self):
        return '<Users {}>'.format(self.email)


@login_manager.user_loader
def load_user(id):
    return Users.query.get(int(id))


class ShippingInfo(db.Model):
    __tablename__ = "shippinginfo"
    id = db.Column(db.Integer, primary_key=True)
    address = db.Column(db.String(200), index=True)
    aditional_indications = db.Column(db.String(200), index=True)
    postcode = db.Column(db.String(12), index=True)
    city = db.Column(db.String(24), index=True)
    state = db.Column(db.String(24), index=True)
    country = db.Column(db.String(24), index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    orders = db.relationship('Orders', backref="orders_shipping")

    def __repr__(self):
        return '<ShippingInfo {}>'.format(self.address1)


class Organizaciones(db.Model):
    __tablename__ = 'organizaciones'
    id = db.Column(db.Integer, primary_key=True)
    organizacion_name = db.Column(db.String(20), index=True)
    organizacion_image = db.Column(db.String(120))
    organizacion_location = db.Column(db.String(120))
    organizacion_phone = db.Column(db.String(15))
    # one to many relationship btwn organizaciones and products
    product = db.relationship('Products', backref='products_organizaciones')

    def __repr__(self):
        return f'<Organizacion {self.organizacion_name} {self.organizacion_location} {self.organizacion_image} {self.organizacion_phone}>'


class Inversionistas(db.Model):
    __tablename__ = 'inversionistas'
    id = db.Column(db.Integer, primary_key=True)
    inversionista_name = db.Column(db.String(20), index=True)
    inversionista_image = db.Column(db.String(120))
    inversionista_desc = db.Column(db.String(120))
    inversionista_email = db.Column(db.String(120))

    def __repr__(self):
        return '<Inversionista {}>'.format(self.organizacion_name)


class Products(db.Model):
    __tablename__ = 'products'
    id = db.Column(db.Integer, primary_key=True)
    product_name = db.Column(db.String(100), index=True)
    product_price = db.Column(db.Integer, index=True)
    product_image = db.Column(db.String(120))
    product_description = db.Column(db.String(200))
    product_stock = db.Column(db.Integer)
    promotion_value = db.Column(db.Integer, index=True)
    organizacion_id = db.Column(db.Integer, db.ForeignKey('organizaciones.id'))

    def __repr__(self):
        return '<Product {}>'.format(self.product_name)


class Kart(db.Model):
    __tablename__ = 'kart'
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'))
    product = db.relationship('Products', uselist=False)
    quantity = db.Column(db.Integer)
    subtotal = db.Column(db.Integer)
    # user and kart is one to one relationship
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    user = db.relationship('Users', uselist=False, backref='users')

    def __repr__(self):
        return '<Cart {}>'.format(self.id)


class Orders(db.Model):
    __tablename__ = 'orders'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    user = db.relationship('Users', uselist=False)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    shippinginfo_id = db.Column(db.Integer, db.ForeignKey('shippinginfo.id'))
    shippinginfo = db.relationship('ShippingInfo', uselist=False)
    kart_id = db.Column(db.Integer, db.ForeignKey('kart.id'))
    kart = db.relationship('Kart', uselist=False)

    def __repr__(self):
        return '<Orders {}>'.format(self.timestamp)


class Eventos(db.Model):
    __tablename__ = 'eventos'
    id = db.Column(db.Integer, primary_key=True)
    evento_name = db.Column(db.String(20), index=True)
    evento_lat = db.Column(db.Float)
    evento_long = db.Column(db.Float)

    def __repr__(self):
        return f'<Evento {self.evento_name}>'
