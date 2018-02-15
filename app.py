#!/Users/Li/virtualenvs/p3/bin/python
"""
flask playground
"""

import os
from flask import Flask, render_template, request, flash
#from wtforms import Form, StringField, TextAreaField, validators
from werkzeug.utils import secure_filename

ALLOWED_EXTENSIONS = set(['csv', 'json'])
APP = Flask(__name__)

@APP.route('/about')
def about():
    """
    about
    """
    return render_template('about.html')

def allowed_file(filename):
    """
    check ext
    """
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@APP.route('/', methods=['GET', 'POST'])
def home():
    """
    home
    """
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part', 'danger')
            return render_template('home.html')
        file = request.files['file']
        if file.filename == '' or not allowed_file(file.filename):
            flash('Not a valid file format', 'danger')
            return render_template('home.html')
        if file and allowed_file(file.filename):
            content = file.read()
            flash('File uploaded', 'success')
            print(content)
    return render_template('home.html')

if __name__ == '__main__':
    APP.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'
    APP.run(debug=True)
