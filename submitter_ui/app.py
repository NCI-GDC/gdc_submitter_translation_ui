# pylint: disable=C0301, C0103, E0611, E0401

"""
flask playground
"""

import random
import string
from flask import Flask, render_template, request, flash

import utils.input as input_utils
import utils.output as output_utils

app = Flask(__name__)

gdc_submission_api = 'https://api.gdc.cancer.gov/v0/submission/_dictionary/'
gdc_submission_template = 'https://api.gdc.cancer.gov/v0/submission/template/'

submission = input_utils.QueryAPI(gdc_submission_api, gdc_submission_template)

@app.route('/about')
def about():
    """
    about page
    """
    return render_template('about.html')

@app.route('/')
def home():
    """
    home page
    """
    return render_template('home.html')

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    """
    step 1
    """
    node_list = submission.get_all_node()
    return render_template('upload.html', node_list=node_list)

@app.route('/mapping', methods=['GET', 'POST'])
def mapping():
    """
    step 2
    """
    snode = str(request.form.get('comp_select'))
    rqlist, oplist, eclist = submission.get_fields(snode)
    enum = submission.get_enum(snode)
    file = request.files['uploadFile']
    if input_utils.file_extention(file.filename) == 'tsv':
        header = file.read().decode("utf-8").strip().split('\n')[0]
        flash('File uploaded, you have selected \"{}\"'.format(snode), 'success')
    else:
        flash('Not a valid file format', 'danger')
        return render_template('mapping.html', selected_node=snode, required_list=[""], optional_list=[""], header="", exclusive_list=[""], enum={})
    return render_template('mapping.html', selected_node=snode, required_list=rqlist, optional_list=oplist, header=header, exclusive_list=eclist, enum=enum)

@app.route('/output/<snode>', methods=['GET', 'POST'])
def output(snode):
    """
    step 3
    """
    user_dict = request.form.to_dict()
    sprop = submission.get_node_json(snode)['properties']
    mapper = output_utils.Mapping(user_dict)
    yaml_style = mapper.get_yaml_with_style("", sprop, snode)
    return render_template('output.html', snode=snode, data=yaml_style)

if __name__ == '__main__':
    app.secret_key = ''.join(random.choices(string.ascii_uppercase + string.digits, k=16))
    app.run(debug=True)
