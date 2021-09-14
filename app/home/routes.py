from app import app, db
from flask import (render_template, request, redirect, url_for, session,
                   flash, Blueprint, abort
                   )

from flask_login import current_user, login_required

from app.models import Organizaciones, Products, Kart
from app.admin.forms import Variations
import random
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
    ids = []
    c = Products.query.filter_by(promotion=True).all()
    for s in c:
        ids.append(s.id)
    sorter = []
    for i in range(3):
        random.randint(1, 1000)
        if i in ids:
            sorter.append(i)

    categories = Organizaciones.query.all()
    products = Products.query.all()

    if current_user.is_anonymous:
        count = 0
    else:
        count = Kart.query.filter_by(user_id=current_user.id).count()

    return render_template("home/index.html", title='Website name',
                           categories=categories, products=products, count=count, sorter=sorter)


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


@home.route('/organizaciones')
def organizaciones():

    page = request.args.get('page', 1, type=int)

    organizaciones = Organizaciones.query\
        .order_by(Organizaciones.organizacion_name).paginate(page=page, per_page=6)

    return render_template("home/organizaciones.html", title="Organizaciones", organizaciones=organizaciones)


@home.route('/organizaciones/<string:organizacion_name>', methods=["GET", "POST"])
def organizacion_details(organizacion_name):

    organizacion = Organizaciones.query.filter_by(
        organizacion_name=organizacion_name).first_or_404()

    return render_template("home/organizacion_details.html",
                           organizacion=organizacion, title=organizacion.organizacion_name)


@home.route('/product/<string:product_name>', methods=["GET", "POST"])
def product_details(product_name):
    if current_user.is_anonymous:
        count = 0
    else:
        count = Kart.query.filter_by(user_id=current_user.id).count()
        user = current_user.id

    form = Variations()

    product_detail = Products.query.filter_by(
        product_name=product_name).first_or_404()

    # add to cart
    if form.validate_on_submit():
        # annonymous users
        if current_user.is_anonymous:
            flash(
                'Please login before you can add items to your shopping cart', 'warning')
            return redirect(url_for("home.product_details", product_name=product_detail.product_name))
        # authenticated users
        cart = Kart(user_id=user, product_id=product_detail.id, quantity=form.amount.data, subtotal=product_detail.product_price)
        db.session.add(cart)
        db.session.commit()

        flash(f"{product_detail.product_name} has been added to cart")
        return redirect(url_for('home.product_details', product_name=product_detail.product_name))
    return render_template("home/productdetails.html",
                           product_detail=product_detail, title=product_detail.product_name,
                           form=form, count=count)
