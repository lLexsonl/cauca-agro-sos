from flask import (render_template, request, redirect, url_for,
                   flash, Blueprint, jsonify
                   )

from app.models import Products, Purchase, Users, Shipping, Kart, Orders

import gc

from flask_login import (current_user, login_required
                         )
from app.users.forms import (ShippingForm, RequestResetForm, ResetPasswordForm,
                             CartForm)
from app import db, mail
from flask_mail import Message
from random import randint

users = Blueprint('users', __name__)


def ShippingPrice():
    '''
    calculate the price of shipping if items is greater than 5 shipping is 2500
    else 1200
    '''
    shipping_price = 0
    if current_user.is_authenticated:
        items = Kart.query.filter_by(user_id=current_user.id).all()
        acum = 0
        for item in items:
            acum += item.quantity
        shipping_price = (int(acum / 10) + 1) * 2500
    return shipping_price


def subtotals():
    subtotals = 0
    if current_user.is_authenticated:
        products = Kart.query.filter_by(user_id=current_user.id).all()
        for product in products:
            subtotals += product.subtotal
    return subtotals


@users.route('/cart', methods=["GET", "POST"])
def cart():
    if current_user.is_anonymous:
        count = 0
        user = 0
        user_info = None
        cartlist = []
        shipping = None
    else:
        user = current_user.id
        user_info = Users.query.get(user)
        count = Kart.query.filter_by(user_id=user).count()
        cartlist = Kart.query.filter_by(user_id=user).all()
        shipping = Shipping.query.filter_by(user_id=user).first()

    form = CartForm()

    price = ShippingPrice()
    items_subtotals = subtotals()

    # for annoymous users
    if current_user.is_anonymous:
        flash('Por favor haz login o registrate para poder utilizar el carrito de compras.')
        return render_template('users/cart.html', count=count, cartlist=cartlist,
                               title="Cart", form=form, price=price, items_subtotals=items_subtotals, shipping=shipping)

    if shipping is None:
        flash('Por favor rellena la información del evio(shipping).')
        return redirect(url_for('users.profile'))

    return render_template('users/cart.html', count=count, cartlist=cartlist,
                           title="Cart", form=form, price=price, items_subtotals=items_subtotals, shipping=shipping, user=user_info)


@users.route('/cart/update/<int:id>', methods=["POST"])
def quantity_update(id):
    cart_item = Kart.query.get_or_404(id)
    quantity = request.form["quantity"]
    cart_item.quantity = quantity
    item_total = cart_item.product.product_price * int(quantity)
    cart_item.subtotal = item_total
    items_subtotal = subtotals()
    db.session.commit()
    gc.collect()
    return jsonify({"result": "success", "item_total": item_total, "subtotal": items_subtotal})


@users.route('/cart/remove/<int:id>', methods=["GET", "POST"])
def remove_item(id):
    cart_item = Kart.query.get_or_404(id)
    db.session.delete(cart_item)
    db.session.commit()
    gc.collect()
    return redirect(url_for('users.cart'))


def send_success_mail(user):
    msg = Message('Item(s) Purchased', sender='noreply@demo.com',
                  recipients=[user.email])
    msg.body = f'''You have successfully purchased items from our store.
These items will be shipped withing 48hours, Thank you.
If you did not make this request simply ignore this request and no changes will be made.
'''
    mail.send(msg)


@login_required
@users.route('/order/<int:user>/<int:shipping>', methods=["GET", "POST"])
def order(user, shipping):

    karts = Kart.query.filter_by(user_id=user).all()


    for kart in karts:
        product = Products.query.get_or_404(kart.product_id)
        product.product_stock = product.product_stock - kart.quantity
        db.session.commit()

        purchase = Purchase(product_id=kart.product_id, quantity=kart.quantity, subtotal=kart.subtotal, user_id=kart.user_id)
        db.session.add(purchase)
        db.session.commit()

        order = Orders(user_id=user, shipping_id=shipping, purchase_id=purchase.id)
        db.session.add(order)
        db.session.commit()

        db.session.delete(kart)
        db.session.commit()

    return redirect(url_for('users.profile'))


@login_required
@users.route('/success', methods=["GET"])
def success():
    u = current_user.id
    flash('Transaction successful', 'success')
    if request.method == "GET":
        user = current_user.email
        send_success_mail(user)
        ref = randint(1, 10000)
        order = Orders(user_id=u, order_ref=ref)
        db.session.add(order)
        db.session.commit()
        items = Kart.query.filter_by(user_id=u).all()
        for i in items:
            ids = i.product
            order.my_orders.append(ids)
            db.session.delete(i)
        db.session.commit()
        gc.collect()
    return render_template('users/charge.html')


@login_required
@users.route('/failure')
def failed():
    flash('transaction Failed', 'danger')
    return render_template('users/failed.html')


@users.route('/profile', methods=["GET", "POST"])
def profile():
    if current_user.is_anonymous:
        count = 0
        user = 0
        orders = None
        items = None
    else:
        user = current_user.id
        count = Kart.query.filter_by(user_id=user).count()
        orders = Orders.query.filter_by(user_id=user).all()
        items = Kart.query.filter_by(user_id=user).all()

    form = ShippingForm()
    shipping = Shipping.query.filter_by(user_id=user).all()
    if form.validate_on_submit():
        info = Shipping(address=form.address.data, aditional_indications=form.additional.data,
                            postcode=form.postcode.data, city=form.city.data,
                            state=form.state.data, country=request.form['country'], user_id=user)
        db.session.add(info)
        db.session.commit()
        gc.collect()
        flash('Shipping information was submitted successfully', 'success')
        return redirect(url_for('users.profile'))
    return render_template('users/profile.html', title="Account page", form=form,
                           shipping=shipping, count=count, orders=orders, items=items)


def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message('Password Reset Request', sender='noreply@demo.com',
                  recipients=[user.email])
    msg.body = f'''To reset your password, visit the following link:
{ url_for('users.reset_token', token = token, _external =True) }
If you did not make this request simply ignore this request and no changes will be made.
'''
    mail.send(msg)


@users.route('/profile/reset_password', methods=["GET", "POST"])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('home.homepage'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash('An email has been sent with instructions to reset you password', 'info')
        return redirect(url_for('auth.login'))
    return render_template('users/reset_request.html', title='Reset password',
                           form=form)


@users.route('/profile/reset_password/<token>', methods=["GET", "POST"])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('home.homepage'))
    user = Users.verify_reset_token(token)
    if user is None:
        flash('That is an invalid or expired token', 'warning')
        return redirect(url_for('users.reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.password_hash = user.set_password(form.password.data)
        db.session.commit()
        gc.collect()
        flash('Your password has been successfully updated', 'success')
        return redirect(url_for('auth.login'))
    return render_template('users/change-password.html', title='Reset password',
                           form=form)
