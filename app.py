#!/Users/Li/virtualenvs/p3/bin/python
"""
flask playground
"""

import json
from flask import Flask, render_template, request, flash, redirect, url_for
from wtforms import Form, TextAreaField, validators

APP = Flask(__name__)

@APP.route('/about')
def about():
    """
    about
    """
    return render_template('about.html')

def file_extention(filename):
    """
    check ext
    """
    return '.' in filename and filename.rsplit('.', 1)[1].lower()

class InputForm(Form):
    """
    form
    """
    inputform = TextAreaField('Or write your input here', [validators.length(min=30)])

@APP.route('/', methods=['GET', 'POST'])
def home():
    """
    home
    """
    form = InputForm(request.form)
    if request.method == 'POST' and form.validate():
        content = str(form['inputform']).rsplit('>')[1].rsplit('<')[0]
        flash('Content uploaded', 'success')
        return redirect(url_for('upload', content=content))
    if request.method == 'POST':
        if 'file' not in request.files:
            return render_template('home.html', form=form)
        file = request.files['file']
        if file:
            if file_extention(file.filename) == 'json':
                content = json.load(file)
                flash('File uploaded', 'success')
                return redirect(url_for('upload', content=content))
            elif file_extention(file.filename) == 'csv':
                content = file.read()
                flash('File uploaded', 'success')
                return redirect(url_for('upload', content=content))
            else:
                flash('Not a valid file format', 'danger')
    return render_template('home.html', form=form)

@APP.route('/upload/<content>')
def upload(content):
    """
    upload
    """
    return render_template('upload.html', content=content)

if __name__ == '__main__':
    APP.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'
    APP.run(debug=True)
