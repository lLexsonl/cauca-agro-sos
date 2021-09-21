from flask_wtf import FlaskForm
from wtforms import (StringField, SubmitField, TextAreaField, IntegerField)
from wtforms.validators import DataRequired, NumberRange, ValidationError
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from flask_wtf.file import FileField, FileAllowed, FileRequired
from app import photos
from app.models import Organizaciones


def positive_number_check(form, field):
    if len(field.data) > 0:
        raise ValidationError('Field must be less than 50 characters')


class OrganizacionForm(FlaskForm):

    name = StringField('Name', [DataRequired()])
    location = StringField('Location', [DataRequired()])
    phone = StringField('Phone', [DataRequired()])
    image = FileField('Organizacion image', validators=[FileRequired(),
                                                        FileAllowed(photos, "images only")])
    submit = SubmitField('Submit')


class InversionistaForm(FlaskForm):

    name = StringField('Name', [DataRequired()])
    image = FileField('Organizacion image', validators=[FileRequired(),
                                                        FileAllowed(photos, "images only")])
    desc = StringField('Description', [DataRequired()])
    email = StringField('Email', [DataRequired()])
    submit = SubmitField('Submit')



class ProductsForm(FlaskForm):
    '''
    Form for admin to add or edit a product
    '''
    organizaciones = QuerySelectField(query_factory=lambda: Organizaciones.query.all(),
                                      get_label="organizacion_name")
    name = StringField('Product name', [DataRequired()])
    price = IntegerField('Product price', [DataRequired(), positive_number_check])
    image = FileField('Product picture', validators=[FileRequired(),
                                                     FileAllowed(photos, "images only")])
    stock = IntegerField('Stock', [DataRequired(), positive_number_check])
    promotion_value = IntegerField(
        'Promotion value', [DataRequired(), NumberRange(0, 100)])
    description = TextAreaField('Description', [
                                DataRequired()])
    submit = SubmitField('Submit')

class EventoForm(FlaskForm):

    name = StringField('Name', [DataRequired()])
    lat = StringField('Latitud', [DataRequired()])
    long = StringField('Longitud', [DataRequired()])
    submit = SubmitField('Submit')


class Variations(FlaskForm):
    amount = IntegerField('Amount', validators=[DataRequired()])
    submit = SubmitField('Add to Cart')
