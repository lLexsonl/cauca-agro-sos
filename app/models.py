from app import db, login_manager, app
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from itsdangerous import TimedJSONWebSignatureSerializer as serializer


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
    order = db.relationship('Orders', backref='user')

    # user and kart is one to one relationship
    kart = db.relationship('Kart', uselist=False, backref='user')

    # one to many relationships with Shipping info
    shipping_info = db.relationship('Shipping', backref='user', lazy='dynamic')

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


class Shipping(db.Model):
    __tablename__ = "shipping"
    id = db.Column(db.Integer, primary_key=True)
    address = db.Column(db.String(200), index=True)
    aditional_indications = db.Column(db.String(200), index=True)
    postcode = db.Column(db.String(12), index=True)
    city = db.Column(db.String(24), index=True)
    state = db.Column(db.String(24), index=True)
    country = db.Column(db.String(24), index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    order = db.relationship('Orders', uselist=False, backref='shipping')

    def __repr__(self):
        return '<Shipping {}>'.format(self.address1)


class Organizaciones(db.Model):
    __tablename__ = 'organizaciones'
    id = db.Column(db.Integer, primary_key=True)
    organizacion_name = db.Column(db.String(20), index=True)
    organizacion_image = db.Column(db.String(120))
    organizacion_location = db.Column(db.String(120))
    organizacion_phone = db.Column(db.String(15))
    # one to many relationship btwn organizaciones and products
    product = db.relationship('Products', backref='organizacion')

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
    subtotal = db.Column(db.Integer) # TODO: Esto se puede quitar
    # user and kart is one to one relationship
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    def __repr__(self):
        return '<Cart {}>'.format(self.id)


class Purchase(db.Model):
    __tablename__ = 'purchase'
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'))
    product = db.relationship('Products', uselist=False)
    quantity = db.Column(db.Integer)
    subtotal = db.Column(db.Integer) # TODO: Esto se puede quitar
    # user and kart is one to one relationship
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    order = db.relationship('Orders', uselist=False, backref='purchase')

    def __repr__(self):
        return '<Cart {}>'.format(self.id)



class Orders(db.Model):
    __tablename__ = 'orders'
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    shipping_id = db.Column(db.Integer, db.ForeignKey('shipping.id'))
    purchase_id = db.Column(db.Integer, db.ForeignKey('purchase.id'))

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
