from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired


class SearchForm(FlaskForm):

    name = StringField('请输入书名:', validators=[DataRequired()])
    submit = SubmitField('搜索')
