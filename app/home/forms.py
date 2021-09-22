from flask_wtf import FlaskForm
from wtforms import SubmitField
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from app.models import Eventos

class SearchEvent(FlaskForm):
    eventos=QuerySelectField(query_factory=lambda: Eventos.query.all(), get_label="evento_name")
    submit=SubmitField('Buscar')
