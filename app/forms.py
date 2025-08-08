from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from flask_wtf.file import FileField, FileAllowed
from wtforms.validators import DataRequired

class PostForm(FlaskForm):
    title = StringField('Post Title', validators=[DataRequired()])
    image = FileField('Upload Image (optional)', validators=[FileAllowed(['jpg', 'png', 'jpeg'])])
    file = FileField('Upload File (optional)')
    submit = SubmitField('Create Post')
