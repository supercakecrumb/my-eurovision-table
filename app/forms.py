from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, IntegerField
from wtforms.validators import DataRequired, NumberRange

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    submit = SubmitField('Login')

class GradeForm(FlaskForm):
    grade = IntegerField('Grade', validators=[DataRequired(), NumberRange(min=0, max=12)])
    submit = SubmitField('Submit')