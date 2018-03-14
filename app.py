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
    node_list = list(x for x in all_node_type.keys() if not x.startswith('_'))
    return render_template('upload.html', node_list=node_list)

@APP.route('/mapping', methods=['GET', 'POST'])
def mapping():
    """
    step 2
    """
    snode = str(request.form.get('comp_select'))
    surl = 'https://api.gdc.cancer.gov/v0/submission/_dictionary/{}'.format(snode)
    #import pdb; pdb.set_trace()
    rplist = rq.get(surl).json()['required']
    sjson = rq.get(surl).json()
    plist = list(sjson['properties'].keys())
    oplist = [x for x in plist if x not in rplist]
    file = request.files['uploadFile']
    if file_extention(file.filename) == 'csv':
        header = file.read().decode("utf-8").strip().split('\n')[0]
        flash('File uploaded, you have selected \"{}\"'.format(snode), 'success')
    else:
        flash('Not a valid file format', 'danger')
        return render_template('mapping.html', selected_node=snode, required_list=[""], optional_list=[""], header="")
    return render_template('mapping.html', selected_node=snode, required_list=rplist, optional_list=oplist, header=header)

@APP.route('/output', methods=['GET', 'POST'])
def output():
    """
    step 3
    """
    user_dict = request.form.to_dict()
    temp_str = """
    {FIELDNAME_IN_THE_NODE}:
        type: {TYPE}
        fieldname:
            - {FIELDNAME_IN_THE_CSV}
    """
    yaml_str = ""
    for key, value in user_dict.items():
        yaml_str += temp_str.format(
            FIELDNAME_IN_THE_NODE=key,
            TYPE="string",
            FIELDNAME_IN_THE_CSV=value
        )
    return render_template('output.html', data=yaml_str)

if __name__ == '__main__':
    APP.secret_key = ''.join(random.choices(string.ascii_uppercase + string.digits, k=16))
    APP.run(debug=True)
