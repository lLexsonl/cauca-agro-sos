from flask_wtf import FlaskForm
from wtforms import (StringField, SubmitField, TextAreaField, IntegerField, validators)
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from flask_wtf.file import FileField, FileAllowed, FileRequired
from app import photos
from app.models import Organizaciones


class OrganizacionForm(FlaskForm):

    name = StringField('Name', [validators.DataRequired()])
    location = StringField('Location', [validators.DataRequired()])
    phone = StringField('Phone', [validators.DataRequired()])
    image = FileField('Organizacion image', validators=[FileRequired(),
                                                        FileAllowed(photos, "images only")])
    submit = SubmitField('Submit')


class InversionistaForm(FlaskForm):

    name = StringField('Name', [validators.DataRequired()])
    image = FileField('Organizacion image', validators=[FileRequired(),
                                                        FileAllowed(photos, "images only")])
    desc = StringField('Description', [validators.DataRequired()])
    email = StringField('Email', [validators.DataRequired()])
    submit = SubmitField('Submit')



class ProductForm(FlaskForm):
    '''
    Form for admin to add or edit a product
    '''
    organizaciones = QuerySelectField(query_factory=lambda: Organizaciones.query.all(),
                                      get_label="organizacion_name")
    name = StringField('Product name', [validators.DataRequired()])
    price = IntegerField('Product price', [validators.DataRequired()])
    image = FileField('Product picture', validators=[FileRequired(),
                                                     FileAllowed(photos, "images only")])
    stock = IntegerField('Stock', [validators.DataRequired()])
    promotion_value = IntegerField(
        'Promotion value', [validators.Optional(strip_whitespace=True), validators.NumberRange(0, 100)])
    description = TextAreaField('Description', [validators.DataRequired()])
    submit = SubmitField('Submit')

class EventoForm(FlaskForm):

    name = StringField('Name', [validators.DataRequired()])
    lat = StringField('Latitud', [validators.DataRequired()])
    long = StringField('Longitud', [validators.DataRequired()])
    submit = SubmitField('Submit')


class Variations(FlaskForm):
    amount = IntegerField('Amount', validators=[validators.DataRequired()])
    submit = SubmitField('Add to Cart')
