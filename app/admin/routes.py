import os
from flask import (flash, render_template, Blueprint, url_for, abort, redirect,
                   request
                   )
from flask_login import current_user, login_required
from app.admin.forms import OrganizacionForm, ProductsForm, InversionistaForm, EventoForm
from app.models import Inversionistas, Organizaciones, Products, Orders, Eventos
from app import photos
from config import Config
import gc
from app import db

admin = Blueprint('admin', __name__)


def check_admin():
    if not current_user.is_admin:
        abort(403)


@admin.route('/organizaciones', methods=['GET', 'POST'])
@login_required
def list_organizaciones():
    '''
    Get all product organizacion
    first check if user is an admin
    '''

    check_admin()

    organizaciones = Organizaciones.query.all()

    return render_template('admin/organizaciones/organizaciones.html', title="Organizaciones", organizaciones=organizaciones)


@admin.route('/organizacion/add', methods=['GET', 'POST'])
def add_organizacion():
    """
    add a organizacion to the
    database
    """
    check_admin()

    add_organizacion = True

    form = OrganizacionForm()

    if form.validate_on_submit():
        name = Organizaciones.query.filter(Organizaciones.organizacion_name==form.name.data).first()
        if name:
            flash("Organizacion already exists.")
            return render_template('admin/organizaciones/organizacion.html', action="Add", form=form,
                           add_organizacion=add_organizacion, title="Add Organizacion")

        filename = request.files['image']
        _, f_ext = os.path.splitext(filename.filename)
        name = form.name.data
        picture_fn = name + f_ext
        photos.save(filename, name=picture_fn)
        url = photos.url(picture_fn)
        organizacion = Organizaciones(
            organizacion_name=form.name.data, organizacion_image=url, organizacion_location=form.location.data, organizacion_phone=form.phone.data)
        try:
            db.session.add(organizacion)
            db.session.commit()
            flash("You have successfully added a new Organizacion")
            gc.collect()
        except Exception:
            flash('Error: Organizacion name already exits. ')

        return redirect(url_for('admin.list_organizaciones'))
    return render_template('admin/organizaciones/organizacion.html', action="Add", form=form,
                           add_organizacion=add_organizacion, title="Add Organizacion")


@admin.route('/organizacion/edit/<int:id>', methods=["GET", "POST"])
def edit_organizacion(id):
    '''
            Edit a organizacion name
    '''

    check_admin()

    add_organizacion = False

    organizacion = Organizaciones.query.get_or_404(id)

    form = OrganizacionForm(obj=organizacion)
    if form.validate_on_submit():
        filename = request.files['image']
        _, f_ext = os.path.splitext(filename.filename)
        name = form.name.data
        picture_fn = name + f_ext
        # get the name of the previous image
        previous_img_name = picture_fn
        photos.save(filename, name=picture_fn)
        url = photos.url(picture_fn)

        organizacion.organizacion_name = form.name.data
        organizacion.organizacion_image = url
        db.session.commit()
        gc.collect()
        flash("You have successfully edited the organizacion")

        # remove the changed picture from the folder
        img_dir = Config.UPLOADED_PHOTOS_DEST+'/'
        os.remove(img_dir+previous_img_name)

        # redirect to the organizacion page
        return redirect(url_for('admin.list_organizaciones'))
    #form.description.data = category.description
    form.name.data = organizacion.organizacion_name

    return render_template('admin/organizacion/organizacion.html', action="Edit",
                           add_organizacion=add_organizacion, form=form,
                           organizacion=organizacion, title="Edit Organizacion")


@admin.route('/organizaciones/delete/<int:id>', methods=["GET", "POST"])
def delete_organizacion(id):
    organizacion = Organizaciones.query.get_or_404(id)

    # get image extension
    _, f_ext = os.path.splitext(organizacion.organizacion_image)

    previous_img_name = organizacion.organizacion_name + f_ext
    img_dir = Config.UPLOADED_PHOTOS_DEST+'/'
    os.remove(img_dir+previous_img_name)
    db.session.delete(organizacion)
    db.session.commit()
    gc.collect()
    flash("You have successfully deleted a Organizacion")

    return redirect(url_for('admin.list_organizaciones'))


'''
	return render_template('admin/organizacion/organizacion.html',
	title = "Delete Organizacion")
'''


@admin.route('/products', methods=['GET'])
@login_required
def list_products():
    check_admin()
    '''
	list all products
	'''
    products = Products.query.all()

    return render_template('admin/products/products.html', title='Products', products=products)


@admin.route('/products/add', methods=["GET", "POST"])
@login_required
def add_product():
    '''
    add a product to the database
    '''

    add_product = True

    form = ProductsForm()
    if form.validate_on_submit():
        filename = request.files['image']
        _, f_ext = os.path.splitext(filename.filename)
        name = form.name.data
        picture_fn = name + f_ext
        photos.save(filename, name=picture_fn)
        url = photos.url(picture_fn)

        product = Products(product_name=form.name.data, product_price=form.price.data, product_image=url,
                           product_description=form.description.data, product_stock=form.stock.data,
                           promotion=form.promotion.data, promotion_value=form.promotion_value.data,
                            organizacion_id=form.organizaciones.data.id,)

        try:
            # add a product to the database
            db.session.add(product)
            db.session.commit()
            gc.collect()
            flash("You have successfully added a product")
        except:
            # in case product name already exists
            flash("Error: product name already exits")

        # redirect to the roles page
        return redirect(url_for('admin.list_products'))
    # load product template
    return render_template('admin/products/product.html', add_product=add_product,
                           form=form, title="Add Product")


@admin.route('/products/edit/<int:id>',  methods=["GET", "POST"])
@login_required
def edit_product(id):
    '''
    edit product
    '''
    check_admin()

    add_product = False

    product = Products.query.get_or_404(id)
    form = ProductsForm(obj=product)
    if form.validate_on_submit():
        filename = request.files['image']
        _, f_ext = os.path.splitext(filename.filename)

        name = form.name.data
        picture_fn = name + f_ext

        # get the name of the previous image
        previous_img_name = picture_fn

        photos.save(filename, name=picture_fn)
        url = photos.url(picture_fn)

        product.product_name = form.name.data
        product.product_price = form.price.data
        product.product_image = url
        product.product_description = form.description.data
        product.product_stock = form.stock.data
        db.session.commit()
        gc.collect()

        # remove the changed picture from the folder
        img_dir = Config.UPLOADED_PHOTOS_DEST+'/'
        os.remove(img_dir+previous_img_name)

        flash('You have successfully edited a product')
        # redirect to the products page
        redirect(url_for('admin.list_products'))

        form.name.data = product.product_name
        form.price.data = product.product_price
        form.image.data = product.product_image
        form.description.data = product.product_description
        form.stock.data = product.product_stock

    return render_template('admin/products/product.html', add_product=add_product,
                           form=form, title="Edit Product")


@admin.route('/products/delete/<int:id>', methods=["GET", "POST"])
@login_required
def delete_product(id):
    '''
    Delete a product from the database
    '''
    check_admin()

    product = Products.query.get_or_404(id)

    # get image extension
    _, f_ext = os.path.splitext(product.product_image)

    previous_img_name = product.product_name+f_ext
    img_dir = Config.UPLOADED_PHOTOS_DEST+'/'
    # remove the changed picture from the folder
    os.remove(img_dir+previous_img_name)

    db.session.delete(product)
    db.session.commit()
    gc.collect()
    flash("You have successfully deleted a product")

    return redirect(url_for('admin.list_products'))


@admin.route('/orders')
@login_required
def list_orders():
    check_admin()
    '''
	list all orders
	'''
    orders = Orders.query.all()

    return render_template('admin/orders.html', title='Orders', orders=orders)

@admin.route('/inversionistas', methods=['GET', 'POST'])
@login_required
def list_inversionistas():
    '''
    Get all product organizacion
    first check if user is an admin
    '''

    check_admin()

    inversionistas = Inversionistas.query.all()

    return render_template('admin/inversionistas/inversionistas.html', title="Inversionistas", inversionistas=inversionistas)


@admin.route('/inversionista/add', methods=['GET', 'POST'])
def add_inversionista():
    """
    add a organizacion to the
    database
    """
    check_admin()

    add_inversionista = True

    form = InversionistaForm()

    if form.validate_on_submit():
        name = Inversionistas.query.filter(Inversionistas.inversionista_nombre==form.name.data).first()
        if name:
            flash("Inversionista already exists.")
            return render_template('admin/inversionistas/inversionista.html', action="Add", form=form,
                           add_inversionista=add_inversionista, title="Add Inversionista")

        filename = request.files['image']
        _, f_ext = os.path.splitext(filename.filename)
        name = form.name.data
        picture_fn = name + f_ext
        photos.save(filename, name=picture_fn)
        url = photos.url(picture_fn)
        inversionista = Inversionistas(
            inversionista_nombre=form.name.data, inversionista_image=url, inversionista_desc=form.desc.data, inversionista_email=form.email.data)
        try:
            db.session.add(inversionista)
            db.session.commit()
            flash("You have successfully added a new Inversionista")
            gc.collect()
        except Exception:
            flash('Error: Inversionista name already exits. ')

        return redirect(url_for('admin.list_inversionistas'))
    return render_template('admin/inversionistas/inversionista.html', action="Add", form=form,
                           add_inversionista=add_inversionista, title="Add Inversionista")


@admin.route('/inversionista/edit/<int:id>', methods=["GET", "POST"])
def edit_inversionista(id):
    '''
            Edit a organizacion name
    '''

    check_admin()

    add_inversionista = False

    inversionista = Inversionistas.query.get_or_404(id)

    form = InversionistaForm(obj=inversionista)
    if form.validate_on_submit():
        filename = request.files['image']
        _, f_ext = os.path.splitext(filename.filename)
        name = form.name.data
        picture_fn = name + f_ext
        # get the name of the previous image
        previous_img_name = picture_fn
        photos.save(filename, name=picture_fn)
        url = photos.url(picture_fn)

        inversionista.inversionista_nombre = form.name.data
        inversionista.inversionista_image = url
        inversionista.inversionista_desc = form.desc.data
        inversionista.inversionista_email = form.email.data
        db.session.commit()
        gc.collect()
        flash("You have successfully edited the organizacion")

        # remove the changed picture from the folder
        img_dir = Config.UPLOADED_PHOTOS_DEST+'/'
        os.remove(img_dir+previous_img_name)

        # redirect to the organizacion page
        return redirect(url_for('admin.list_organizaciones'))
    #form.description.data = category.description
    form.name.data = inversionista.name

    return render_template('admin/inversionistas/inversionista.html', action="Edit",
                           add_inversionista=add_inversionista, form=form,
                           inversionista=inversionista, title="Edit Inversionista")


@admin.route('/inversionista/delete/<int:id>', methods=["GET", "POST"])
def delete_inversionista(id):
    inversionista = Inversionistas.query.get_or_404(id)

    # get image extension
    _, f_ext = os.path.splitext(inversionista.inversionista_image)

    previous_img_name = inversionista.inversionista_nombre + f_ext
    img_dir = Config.UPLOADED_PHOTOS_DEST+'/'
    os.remove(img_dir+previous_img_name)
    db.session.delete(inversionista)
    db.session.commit()
    gc.collect()
    flash("You have successfully deleted a Organizacion")

    return redirect(url_for('admin.list_inversionistas'))


@admin.route('/eventos', methods=['GET', 'POST'])
@login_required
def list_eventos():
    '''
    Get all product organizacion
    first check if user is an admin
    '''

    check_admin()

    eventos = Eventos.query.all()

    return render_template('admin/eventos/eventos.html', title="Eventos", eventos=eventos)


@admin.route('/eventos/add', methods=['GET', 'POST'])
def add_evento():
    """
    add a evento to the database
    """
    check_admin()

    add_evento = True

    form = EventoForm()

    if form.validate_on_submit():
        name = Eventos.query.filter(Eventos.evento_name==form.name.data).first()
        if name:
            flash("Evento already exists.")
            return render_template('admin/eventos/evento.html', action="Add", form=form,
                           add_evento=add_evento, title="Add Evento")

        evento = Eventos(
            evento_name=form.name.data, evento_lat=form.lat.data, evento_long=form.long.data)
        try:
            db.session.add(evento)
            db.session.commit()
            flash("You have successfully added a new evento")
            gc.collect()
        except Exception:
            flash('Error: Evento name already exits.')

        return redirect(url_for('admin.list_eventos'))
    return render_template('admin/eventos/evento.html', action="Add", form=form,
                           add_evento=add_evento, title="Add Evento")


@admin.route('/evento/edit/<int:id>', methods=["GET", "POST"])
def edit_evento(id):
    '''
        Edit a evento
    '''

    check_admin()

    add_evento = False

    evento = Eventos.query.get_or_404(id)

    form = EventoForm(obj=evento)
    if form.validate_on_submit():

        evento.evento_name = form.name.data
        evento.evento_lat = form.lat.data
        evento.evento_long = form.long.data
        db.session.commit()
        gc.collect()
        flash("You have successfully edited the evento")

        return redirect(url_for('admin.list_eventos'))

    return render_template('admin/eventos/evento.html', action="Edit",
                           add_evento=add_evento, form=form,
                           evento=evento, title="Edit Evento")


@admin.route('/evento/delete/<int:id>', methods=["GET", "POST"])
def delete_evento(id):
    evento = Eventos.query.get_or_404(id)

    db.session.delete(evento)
    db.session.commit()
    gc.collect()
    flash("You have successfully deleted a evento")

    return redirect(url_for('admin.list_eventos'))
