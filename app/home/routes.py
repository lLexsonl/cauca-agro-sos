from app import app, db
from flask import (render_template, request, redirect, url_for, session,
                   flash, Blueprint, abort, json
                   )

from flask_login import current_user, login_required

from app.models import Inversionistas, Organizaciones, Products, Kart, Eventos
from app.admin.forms import Variations
from app.home.forms import SearchEvent

home = Blueprint('home', __name__)


@home.route('/admin/dashboard', methods=['GET'])
@login_required
def admin_dashboard():
    # preventing non admins from accessing the page
    if not current_user.is_admin:
        abort(403)
    return render_template('admin/admin_dashboard.html', title="Dashboard")


@home.route('/', methods=['GET'])
def landing():
    return redirect(url_for("home.homepage"))


@home.route('/home', methods=['GET'])
def homepage():
    products = Products.query.all()
    products = [product for product in products if product.promotion_value > 0]

    if current_user.is_anonymous:
        count = 0
    else:
        count = Kart.query.filter_by(user_id=current_user.id).count()

    return render_template("home/index.html", title='Website name',
                           products=products, count=count, size=len(products))


@home.route('/canasta')
def canasta():
    if current_user.is_anonymous:
        count = 0
    else:
        count = Kart.query.filter_by(user_id=current_user.id).count()

    page = request.args.get('page', 1, type=int)

    products = Products.query\
        .order_by(Products.product_name).paginate(page=page, per_page=6)

    return render_template("home/canasta.html", title="Canasta Agricola", products=products, count=count)


@home.route('/organizacion')
def organizaciones():

    if current_user.is_anonymous:
        count = 0
    else:
        count = Kart.query.filter_by(user_id=current_user.id).count()

    page = request.args.get('page', 1, type=int)

    organizaciones = Organizaciones.query\
        .order_by(Organizaciones.organizacion_name).paginate(page=page, per_page=6)

    return render_template("home/organizaciones.html", title="Organizaciones", organizaciones=organizaciones, count=count)


@home.route('/organizacion/<int:id>', methods=["GET", "POST"])
def organizacion_details(id):

    if current_user.is_anonymous:
        count = 0
    else:
        count = Kart.query.filter_by(user_id=current_user.id).count()

    organizacion = Organizaciones.query.filter_by(id=id).first_or_404()

    return render_template("home/organizacion_details.html",
                           organizacion=organizacion, title=organizacion.organizacion_name, count=count)


@home.route('/product/<int:id>', methods=["GET", "POST"])
def product_details(id):
    if current_user.is_anonymous:
        count = 0
    else:
        count = Kart.query.filter_by(user_id=current_user.id).count()
        user = current_user.id

    form = Variations()

    product_detail = Products.query.filter_by(id=id).first_or_404()
    organizacion = Organizaciones.query.filter_by(id=product_detail.organizacion_id).first_or_404()

    form.amount.choices = [i+1 for i in range(product_detail.product_stock)]

    # add to cart
    if form.validate_on_submit():
        # annonymous users
        if current_user.is_anonymous:
            flash(
                'Please login before you can add items to your shopping cart', 'warning')
            return redirect(url_for("home.product_details", id=product_detail.id))
        # authenticated users
        subtotal = (int(form.amount.data)) * (product_detail.product_price - (product_detail.product_price * (product_detail.promotion_value/100)))
        cart = Kart(user_id=user, product_id=product_detail.id,
                    quantity=form.amount.data, subtotal=subtotal)
        db.session.add(cart)
        db.session.commit()

        flash(f"{product_detail.product_name} has been added to cart")
        return redirect(url_for('home.product_details', id=product_detail.id))
    return render_template("home/productdetails.html",
                           product_detail=product_detail, title=product_detail.product_name,
                           form=form, count=count, organizacion=organizacion)


@home.route('/inversionista')
def inversionistas():

    if current_user.is_anonymous:
        count = 0
    else:
        count = Kart.query.filter_by(user_id=current_user.id).count()


    page = request.args.get('page', 1, type=int)

    inversionistas = Inversionistas.query\
        .order_by(Inversionistas.inversionista_name).paginate(page=page, per_page=6)

    return render_template("home/inversionistas.html", title="Inversionistas", inversionistas=inversionistas, count=count)


@home.route('/inversionista/<int:inversionista_id>', methods=["GET", "POST"])
def inversionista_details(inversionista_id):

    if current_user.is_anonymous:
        count = 0
    else:
        count = Kart.query.filter_by(user_id=current_user.id).count()

    inversionista = Inversionistas.query.filter_by(
        id=inversionista_id).first_or_404()

    return render_template("home/inversionista_details.html",
                           inversionista=inversionista, title=inversionista.inversionista_name, count=count)


@home.route('/eventos', methods=["GET", "POST"])
def eventos():

    if current_user.is_anonymous:
        count = 0
    else:
        count = Kart.query.filter_by(user_id=current_user.id).count()

    long = -76.60631917174642
    lat = 2.4419131406694277
    zoom = 12.5
    eventos = Eventos.query.all()
    form = SearchEvent()
    if form.validate_on_submit():
        long = form.eventos.data.evento_long
        lat = form.eventos.data.evento_lat
        zoom = 15
    return render_template("home/eventos.html", title="Eventos", form=form, eventos=eventos, long=long, lat=lat, zoom=zoom, count=count)
