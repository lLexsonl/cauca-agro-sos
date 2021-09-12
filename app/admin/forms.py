from flask_wtf import FlaskForm
from wtforms import (StringField, SubmitField, TextAreaField, IntegerField,
                     FloatField, validators, RadioField, BooleanField
                     )
from wtforms.validators import DataRequired, Email
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from flask_wtf.file import FileField, FileAllowed, FileRequired
from app import photos
from app.models import Organizaciones


class OrganizacionForm(FlaskForm):

    name = StringField('Name', [validators.DataRequired()])
    location = StringField('Location', [validators.DataRequired(), Email()])
    email = StringField('Email', [validators.DataRequired()])
    image = FileField('Organizacion Image', validators=[FileRequired(),
                                                        FileAllowed(photos, "images only")])
    submit = SubmitField('Submit')


class ProductsForm(FlaskForm):
    '''
    Form for admin to add or edit a product
    '''
    organizaciones = QuerySelectField(query_factory=lambda: Organizaciones.query.all(),
                                      get_label="organizacion")
    name = StringField('Product name', [validators.DataRequired()])
    price = IntegerField('Product Price', [validators.DataRequired()])
    image = FileField('Product picture', validators=[FileRequired(),
                                                     FileAllowed(photos, "images only")])
    stock = IntegerField('Stock', [validators.DataRequired()])
    promotion = BooleanField('Promotion', [validators.DataRequired()])
    promotion_value = IntegerField(
        'Promotion Value', [validators.DataRequired()])
    description = TextAreaField('Describe the product', [
                                validators.DataRequired()])
    submit = SubmitField('Submit')


class Variations(FlaskForm):
    sizes = RadioField('Sizes', validators=[DataRequired(message="select a product size")],
                       choices=[('Small', 'S'), ('Medium', 'M'), ('Large', 'L'), ('Extra Large', 'XL')])
    submit = SubmitField('Add to Cart')
