# pylint: disable=C0103

"""
flask playground
"""

import uuid
from flask import Flask, render_template, request, flash

import utils.input as input_utils
import utils.output as output_utils

app = Flask(__name__)

gdc_submission_api = 'https://api.gdc.cancer.gov/v0/submission/_dictionary/'
gdc_submission_template = 'https://api.gdc.cancer.gov/v0/submission/template/'

submission = input_utils.QueryAPI(gdc_submission_api, gdc_submission_template)

@app.route('/about')
def about():
    '''about page'''
    return render_template('about.html')

@app.route('/')
def home():
    '''home page'''
    return render_template('home.html')

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    '''upload tsv'''
    node_list = submission.get_all_node()
    return render_template('upload.html', node_list=node_list)

@app.route('/mapping', methods=['GET', 'POST'])
def mapping():
    '''select fields'''
    snodes = request.form.getlist('comp_select[]')
    nodes_str = '&'.join(snodes)
    sdict = submission.get_nodes_dict(snodes)
    ufile = request.files['uploadFile']
    if input_utils.file_extention(ufile.filename) == 'tsv':
        header = ufile.read().decode("utf-8").strip().split('\n')[0]
        flash('File uploaded, you have selected {}'\
             .format([x.encode('ascii', 'ignore') for x in snodes]), 'success')
    else:
        flash('Not a valid file format', 'danger')
        return render_template('mapping.html', header="", nodes_dict=sdict, snodes=nodes_str)
    return render_template('mapping.html', header=header, nodes_dict=sdict, snodes=nodes_str)

@app.route('/output/<snodes>', methods=['GET', 'POST'])
def output(snodes):
    '''preview/download outputs'''
    user_dict = request.form.to_dict()
    snode_list = snodes.split('&')
    mapper = output_utils.Mapping(user_dict)
    all_yaml_dict = {}
    for node in snode_list:
        sprop = submission.get_node_json(node)['properties']
        yaml_str = output_utils.get_style(mapper.get_yaml_string("", sprop, node))
        all_yaml_dict[node] = yaml_str
    conf_str = output_utils.get_style(mapper.get_conf_string(snode_list))
    to_be_deleted_str = output_utils.get_style(mapper.get_tbd_string(snode_list))
    return render_template('output.html', all_yaml_dict=all_yaml_dict, \
                            conf_data=conf_str, to_be_deleted_data=to_be_deleted_str)

if __name__ == '__main__':
    app.secret_key = uuid.uuid4().hex
    app.run(debug=True)
