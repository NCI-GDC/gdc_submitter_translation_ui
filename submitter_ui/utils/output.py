# pylint: disable=R0901
'''output utils'''

import yaml

class MyDumper(yaml.Dumper):
    '''customize indent dumper'''
    def increase_indent(self, flow=False, indentless=False):
        return super(MyDumper, self).increase_indent(flow, False)

def get_style(yaml_string):
    '''get yaml with style'''
    yaml_style = yaml.dump(yaml.load(yaml_string), \
                 Dumper=MyDumper, indent=4, default_flow_style=False)
    return yaml_style

def save_type(dct):
    '''save type'''
    value = dct.get('type')
    if isinstance(value, list):
        return tuple(value)
    return value

def get_type(dct):
    '''get type'''
    if save_type(dct) is None:
        for dict_value in dct.values():
            if isinstance(dict_value, dict):
                type_ = save_type(dict_value)
            elif isinstance(dict_value, list):
                type_ = "list"
            else:
                type_ = None
    else:
        type_ = save_type(dct)
    return type_

def remove_dict_key_prefix(dct, prefix):
    '''remove dict key prefix'''
    new_key = []
    for key in dct.keys():
        if key.startswith(prefix):
            new_key.append(key[len(prefix):])
    if new_key:
        new_dict = {k: dct[prefix + k] for k in new_key}
    else: new_dict = {}
    return new_dict

class Mapping(object):
    '''this class describes some methods prepare output yaml/conf file'''
    def __init__(self, node_list, user_dict):
        self.node_list = node_list
        self.user_dict = user_dict
        self.temp_str = """
        {FIELDNAME_IN_THE_NODE}:
            type: {TYPE}
            fieldname:
                - {FIELDNAME_IN_THE_TSV}
        """
        self.conf_str = """
        base_field_name: not_defined
        project_id:
            fieldname: {PROJECT_ID_IN_TSV}
        node_links:"""
        self.conf_id_str = """
          - {SNODE}:
              links_to: {FIELDNAME_IN_THE_NODE}
              fieldname: {FIELDNAME_IN_THE_TSV}"""
        self.conf_submitter_id_str = """
          - {SNODE}:
              fieldname: {FIELDNAME_IN_THE_TSV}
              tag: {FIELDNAME_IN_THE_NODE}
              linker: submitter_id"""
        self.to_be_deleted_str = """
        {LIST_NAME}:
          type: collective_list
          source_row: True
          source_field: {SOURCE_FIELD}
          fieldname:
              - not_defined
          tag: {ID_TYPE}/{SNODE}"""

    def create_output_dict(self):
        '''create output dict for all the selected nodes'''
        output_dict = {node: "" for node in self.node_list }
        return output_dict

    def _get_dict_for_yaml(self, snode):
        '''get part of the user dict from html for yaml output'''
        dict_for_node = {key: value for key, value in self.user_dict.items() \
                        if key.startswith("{}_".format(snode))}
        renamed_node_dict = remove_dict_key_prefix(dict_for_node, "{}_".format(snode))
        dict_for_yaml = {key: value for key, value in renamed_node_dict.items() \
                        if not key.startswith("link_") and not key.startswith("tbd_")}
        return dict_for_yaml

    def _get_dict_for_conf(self):
        '''get part of the user dict from html for conf output'''
        dict_for_conf = {key: value for key, value in self.user_dict.items() \
                        if key.startswith("link_")}
        return dict_for_conf

    def get_dict_for_delete_yaml(self):
        '''get part of the user dict from html for to_be_deleted.yaml'''
        dict_for_tbd = {key: value for key, value in self.user_dict.items() \
                        if key.startswith("tbd_")}
        return dict_for_tbd

    def _remap_dict(self, snode):
        '''remap dict for conf ouptut'''
        new_dict = remove_dict_key_prefix(self._get_dict_for_conf(), 'link_')
        if any(k.startswith("exclusive_") for k in new_dict.keys()):
            remap = {}
            for key, value in new_dict.items():
                if key.startswith('exclusive_field_'):
                    key_index = key.split('_')[-1]
                    remap[value] = key_index
            for key, value in new_dict.items():
                if key.startswith("exclusive_chosen_"):
                    for key_, value_ in remap.items():
                        if value_ in key:
                            remap[key_] = value
            remap['id_type'] = new_dict['id_type']
        else:
            remap = new_dict
        if self._get_dict_for_yaml(snode).get('project_id'):
            remap['project_id'] = self._get_dict_for_yaml(snode)['project_id']
        else: remap['project_id'] = 'not_defined'
        return remap

    def get_yaml_string(self, yaml_str, nodeprops, snode):
        '''get yaml output'''
        s3_loc_str = """
        s3_loc:
            type: string
            upload_field: true
            skip_upload: false
            fieldname:
                - {FIELDNAME_IN_THE_TSV}
        """
        default_str = """    default_value: {DEFAULT}"""
        subtype_str = """    subtype: {SUBTYPE}"""
        no_generate_str = """    no_generate: True"""
        trans_type = {
            ('integer', 'null'): 'int',
            ('number', 'null'): 'int',
            ('string',): 'string',
            'boolean': 'boolean',
            'integer': 'int',
            'number': 'int',
            'string': 'string'
            }
        enum_dict = remove_dict_key_prefix(self._get_dict_for_yaml(), 'default_')
        for key, value in self._get_dict_for_yaml().items():
            if not key.startswith('default_'):
                if enum_dict.get(key):
                    temp_d_str = self.temp_str + default_str
                    yaml_str += temp_d_str.format(
                        FIELDNAME_IN_THE_NODE=key,
                        TYPE="string",
                        FIELDNAME_IN_THE_TSV=value,
                        DEFAULT=enum_dict[key]
                    )
                elif key == 'submitter_id':
                    temp_d_str = self.temp_str + no_generate_str
                    yaml_str += temp_d_str.format(
                        FIELDNAME_IN_THE_NODE=key,
                        TYPE="string",
                        FIELDNAME_IN_THE_TSV=value
                    )
                elif key == 'type':
                    if value == 'not_defined':
                        temp_d_str = self.temp_str + default_str
                        yaml_str += temp_d_str.format(
                            FIELDNAME_IN_THE_NODE=key,
                            TYPE="string",
                            FIELDNAME_IN_THE_TSV=value,
                            DEFAULT=snode
                        )
                    else:
                        temp_d_str = self.temp_str
                        yaml_str += temp_d_str.format(
                            FIELDNAME_IN_THE_NODE=key,
                            TYPE="string",
                            FIELDNAME_IN_THE_TSV=value
                        )
                elif key == 's3_loc':
                    yaml_str += s3_loc_str.format(FIELDNAME_IN_THE_TSV=value)
                else:
                    if get_type(nodeprops[key]) == 'list':
                        temp_d_str = self.temp_str + subtype_str
                        yaml_str += temp_d_str.format(
                            FIELDNAME_IN_THE_NODE=key,
                            TYPE='list',
                            FIELDNAME_IN_THE_TSV=value,
                            SUBTYPE='dict'
                        )
                    else:
                        yaml_str += self.temp_str.format(
                            FIELDNAME_IN_THE_NODE=key,
                            TYPE=trans_type.get(get_type(nodeprops[key])),
                            FIELDNAME_IN_THE_TSV=value
                        )
        return yaml_str

    def get_conf_string(self, snode):
        '''get conf string'''
        conf_del_str = """
        collective_nodes:
          - to_be_deleted:
                links_to: not_defined
        """
        conf_dict = self._remap_dict()
        if conf_dict['id_type'] == 'submitter_id':
            conf_style = self.conf_submitter_id_str
        else: conf_style = self.conf_id_str
        conf_dict.pop('id_type')
        conf_str = self.conf_str.format(PROJECT_ID_IN_TSV=conf_dict['project_id'])
        conf_dict.pop('project_id')
        output_str = ""
        for key, value in conf_dict.items():
            output_str += conf_style.format(
                SNODE=snode,
                FIELDNAME_IN_THE_NODE=key,
                FIELDNAME_IN_THE_TSV=value
            )
        conf_str += output_str
        if self.get_dict_for_delete_yaml():
            conf_str += conf_del_str
        return conf_str

    def get_tbd_string(self, snode):
        '''get to_be_deleted.yaml string'''
        to_be_deleted_bot_str = """
        submitter_id:
          type: string
          fieldname:
            - not_defined
          no_generate: True
        type:
          type: string
          fieldname:
            - not_defined
          default_value: to_be_deleted
        """
        tbd_dict = self.get_dict_for_delete_yaml()
        list_name = snode.lower() + '_list'
        tbd_str = self.to_be_deleted_str.format(
            LIST_NAME=list_name,
            ID_TYPE=tbd_dict['tbd_id_type'],
            SOURCE_FIELD=tbd_dict['tbd_source_field'],
            SNODE=snode
        )
        return tbd_str + to_be_deleted_bot_str
