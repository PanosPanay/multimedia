from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import SubmitField

class UploadForm(FlaskForm):
    """上传表单"""
    file = FileField('上传文件', validators=[FileRequired(), 
        FileAllowed(['docx', 'pdf', 'wav', 'aac', 'jpg', 'png', 'psb', 'psd', 'bmp', 'py', 'fla', 'swf', 'txt', 'md', 'zip', 'rar', '7z'])])
    submit = SubmitField()