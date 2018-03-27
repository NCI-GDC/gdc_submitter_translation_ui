#!/Users/Li/virtualenvs/p3/bin/python
# pylint: disable=C0301, C0103, R0901

"""
flask playground
"""

import random
import string
import yaml
import requests as rq
from flask import Flask, render_template, request, flash

class MyDumper(yaml.Dumper):
    """
    customize indent dumper
    """
    def increase_indent(self, flow=False, indentless=False):
        return super(MyDumper, self).increase_indent(flow, False)

def file_extention(filename):
    """
    check ext
    """
    return '.' in filename and filename.rsplit('.', 1)[1].lower()

def get_fields(node=None):
    """
    check template
    """
    surl = 'https://api.gdc.cancer.gov/v0/submission/_dictionary/{}'.format(node)
    sdict = rq.get(surl).json()
    rqlist = []
    if sdict.get('required'):
        rqlist = sdict['required']
    stemp = 'https://api.gdc.cancer.gov/v0/submission/template/{}?format=json'.format(str(node))
    tplist = list(rq.get(stemp).json().keys())
    required = [x for x in rqlist if x in tplist]
    oplist = [y for y in tplist if y not in rqlist]
    exclusive_pairs = []
    if sdict.get('links'):
        for pair in sdict['links']:
            if pair.get('exclusive'):
                if pair['exclusive'] is True:
                    exclusive_pairs.append([d['name'] for d in pair['subgroup']])
    dup = [i for j in exclusive_pairs for i in j]
    optional = [z for z in oplist if z not in dup]
    return (required, optional, exclusive_pairs)

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
        ('string', 'null'): 'string',
        'array': 'list',
        'string': 'string',
        'number': 'int',
        'null': 'null'
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
                TYPE="string",
                FIELDNAME_IN_THE_CSV=value
            )
    return yaml_str


app = Flask(__name__)

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
    all_node_type = rq.get('https://api.gdc.cancer.gov/v0/submission/_dictionary/_all').json()
    node_list = list(x for x in all_node_type.keys() if not x.startswith('_'))
    return render_template('upload.html', node_list=node_list)

@app.route('/mapping', methods=['GET', 'POST'])
def mapping():
    """
    step 2
    """
    snode = str(request.form.get('comp_select'))
    rqlist, oplist, eclist = get_fields(node=snode)
    file = request.files['uploadFile']
    if file_extention(file.filename) == 'csv':
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
