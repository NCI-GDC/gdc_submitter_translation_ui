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
    snode = str(request.form.get('comp_select'))
    rqlist, oplist, eclist, ielist, llist = submission.get_fields(snode)
    enum = submission.get_enum(snode)
    ufile = request.files['uploadFile']
    if input_utils.file_extention(ufile.filename) == 'tsv':
        header = ufile.read().decode("utf-8").strip().split('\n')[0]
        flash('File uploaded, you have selected \"{}\"'.format(snode), 'success')
    else:
        flash('Not a valid file format', 'danger')
        return render_template('mapping.html', header="", \
               selected_node=snode, required_list=[], optional_list=[], \
               exclusive_list=[], inexclusive_list=[], link_list=[], enum={})
    return render_template('mapping.html', header=header, \
           selected_node=snode, required_list=rqlist, optional_list=oplist, \
           exclusive_list=eclist, inexclusive_list=ielist, link_list=llist, enum=enum)

@app.route('/output/<snode>', methods=['GET', 'POST'])
def output(snode):
    '''preview/download outputs'''
    user_dict = request.form.to_dict()
    sprop = submission.get_node_json(snode)['properties']
    mapper = output_utils.Mapping(user_dict)
    yaml_str = output_utils.get_style(mapper.get_yaml_string("", sprop, snode))
    conf_str = output_utils.get_style(mapper.get_conf_string(snode))
    if mapper.get_dict_for_delete_yaml():
        tbd_str = output_utils.get_style(mapper.get_tbd_string(snode))
    else: tbd_str = ""
    return render_template('output.html', snode=snode, yaml_data=yaml_str, \
                           conf_data=conf_str, to_be_deleted=tbd_str)

if __name__ == '__main__':
    app.secret_key = uuid.uuid4().hex
    app.run(debug=True)
