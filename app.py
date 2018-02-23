#!/Users/Li/virtualenvs/p3/bin/python
"""
flask playground
"""

import random
import string
import requests as rq
from flask import Flask, render_template, request, flash

def file_extention(filename):
    """
    check ext
    """
    return '.' in filename and filename.rsplit('.', 1)[1].lower()

APP = Flask(__name__)

@APP.route('/about')
def about():
    """
    about page
    """
    return render_template('about.html')

@APP.route('/')
def home():
    """
    home page
    """
    return render_template('home.html')

@APP.route('/upload', methods=['GET', 'POST'])
def upload():
    """
    step 1
    """
    all_node_type = rq.get('https://api.gdc.cancer.gov/v0/submission/_dictionary/_all').json()
    node_list = []
    for key, value in all_node_type.items():
        if not key.startswith('_'):
            node_list.append(key)
    return render_template('upload.html', node_list=node_list)

@APP.route('/mapping', methods=['GET', 'POST'])
def mapping():
    """
    step 2
    """
    snode = str(request.form.get('comp_select'))
    surl = 'https://api.gdc.cancer.gov/v0/submission/_dictionary/{}'.format(snode)
    plist = []
    sjson = rq.get(surl).json()
    for key, value in sjson.items():
        if not key.startswith('$'):
            plist.append(key)
    file = request.files['uploadFile']
    if file_extention(file.filename) == 'csv':
        header = file.read().decode("utf-8").strip().split('\n')[0]
        flash('File uploaded', 'success')
    else:
        flash('Not a valid file format', 'danger')
        return render_template('mapping.html', selected_node=snode, property_list=[""], header="")
    return render_template('mapping.html', selected_node=snode, property_list=plist, header=header)


if __name__ == '__main__':
    APP.secret_key = ''.join(random.choices(string.ascii_uppercase + string.digits, k=16))
    APP.run(debug=True)
