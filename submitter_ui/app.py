# pylint: disable=C0301, C0103, E0611, E0401

"""
flask playground
"""

import random
import string
import yaml
import requests as rq
from flask import Flask, render_template, request, flash

import utils.input as input_utils
from utils.output import MyDumper



def save_type(dct=None):
    """
    save type
    """
    value = dct.get('type')
    if isinstance(value, list):
        return tuple(value)
    return value

def get_type(dct=None, type_list=None):
    """
    get type
    """
    # for dct in anyOf_dict_list:
    check_list = ['anyOf', 'oneOf']
    if set(dct.keys()).intersection(check_list):
        for key in set(dct.keys()).intersection(check_list):
            for d in dct[key]:
                type_list.append(save_type(dct=d))
                for dict_value in d.values():
                    if isinstance(dict_value, dict):
                        type_list.append(save_type(dct=dict_value))
                        get_type(dct=dict_value, type_list=type_list)
    else:
        type_list.append(save_type(dct=dct))
        for dict_value in dct.values():
            if isinstance(dict_value, dict):
                type_list.append(save_type(dct=dict_value))
                get_type(dct=dict_value, type_list=type_list)

def remap_dict(to_remap=None):
    """
    remap dict
    """
    remap = {}
    for key, value in to_remap.items():
        if key.startswith('exclusive_field_'):
            key_index = key.split('_')[-1]
            remap[value] = key_index
    for key, value in to_remap.items():
        if key.startswith("exclusive_chosen_"):
            for k, v in remap.items():
                if v in key:
                    remap[k] = value
    return remap

def get_yaml(user_dict=None, yaml_str=None, nodejson=None):
    """
    get yaml
    """
    temp_str = """
    {FIELDNAME_IN_THE_NODE}:
        type: {TYPE}
        fieldname:
            - {FIELDNAME_IN_THE_CSV}
    """
    trans_type = {
        ('string',): 'string',
        ('string', 'null'): 'string',
        'array': 'list',
        'string': 'string',
        'number': 'int',
        'null': 'null',
        'integer': 'int'
    }
    for key, value in user_dict.items():
        stype = []
        get_type(nodejson['properties']['{}'.format(key)], stype)
        typelist = list(set(stype))
        if None in typelist:
            typelist.remove(None)
        if bool(typelist):
            yaml_str += temp_str.format(
                FIELDNAME_IN_THE_NODE=key,
                TYPE=[trans_type[x] for x in typelist if x in trans_type.keys()],
                FIELDNAME_IN_THE_CSV=value
            )
        else:
            yaml_str += temp_str.format(
                FIELDNAME_IN_THE_NODE=key,
                TYPE=["string"],
                FIELDNAME_IN_THE_CSV=value
            )
    return yaml_str


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
    file = request.files['uploadFile']
    if input_utils.file_extention(file.filename) == 'tsv':
        header = file.read().decode("utf-8").strip().split('\n')[0]
        flash('File uploaded, you have selected \"{}\"'.format(snode), 'success')
    else:
        flash('Not a valid file format', 'danger')
        return render_template('mapping.html', selected_node=snode, required_list=[""], optional_list=[""], header="", exclusive_list=[""])
    return render_template('mapping.html', selected_node=snode, required_list=rqlist, optional_list=oplist, header=header, exclusive_list=eclist)

@app.route('/output/<snode>', methods=['GET', 'POST'])
def output(snode):
    """
    step 3
    """
    user_dict = request.form.to_dict()
    surl = 'https://api.gdc.cancer.gov/v0/submission/_dictionary/{}'.format(snode)
    sjson = rq.get(surl).json()
    easy_dict = {key: value for key, value in user_dict.items() if not key.startswith("exclusive_")}
    exclusive_dict = {key: value for key, value in user_dict.items() if key.startswith("exclusive_")}
    exclusive_str = ""
    if exclusive_dict:
        exclusive_remap = remap_dict(to_remap=exclusive_dict)
        exclusive_str = get_yaml(user_dict=exclusive_remap, yaml_str="", nodejson=sjson)
    full_yaml_str = get_yaml(user_dict=easy_dict, yaml_str=exclusive_str, nodejson=sjson)
    yaml_style = yaml.dump(yaml.load(full_yaml_str), Dumper=MyDumper, indent=4, default_flow_style=False)
    return render_template('output.html', snode=snode, data=yaml_style)

if __name__ == '__main__':
    app.secret_key = ''.join(random.choices(string.ascii_uppercase + string.digits, k=16))
    app.run(debug=True)
