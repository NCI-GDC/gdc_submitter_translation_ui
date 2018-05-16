# pylint: disable=R0901
'''output utils'''

import yaml

class MyDumper(yaml.Dumper):
    '''customize indent dumper'''
    def increase_indent(self, flow=False, indentless=False):
        return super(MyDumper, self).increase_indent(flow, False)

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

class Mapping(object):
    '''this class describes some methods prepare output yaml/conf file'''
    def __init__(self, user_dict):
        self.user_dict = user_dict

    def _get_dict_for_yaml(self):
        '''get part of the user dict from html for yaml output'''
        dict_for_yaml = {key: value for key, value in self.user_dict.items() \
                        if not key.startswith("exclusive_")}
        return dict_for_yaml

    def _get_dict_for_conf(self):
        '''get part of the user dict from html for conf output'''
        dict_for_conf = {key: value for key, value in self.user_dict.items() \
                        if key.startswith("exclusive_")}
        return dict_for_conf

    def _remap_dict(self):
        '''remap dict for conf ouptut'''
        remap = {}
        for key, value in self._get_dict_for_conf().items():
            if key.startswith('exclusive_field_'):
                key_index = key.split('_')[-1]
                remap[value] = key_index
        for key, value in self._get_dict_for_conf().items():
            if key.startswith("exclusive_chosen_"):
                for key_, value_ in remap.items():
                    if value_ in key:
                        remap[key_] = value
        return remap

    def get_yaml_string(self, yaml_str, nodeprops, snode):
        '''get yaml output'''
        temp_str = """
        {FIELDNAME_IN_THE_NODE}:
            type: {TYPE}
            fieldname:
                - {FIELDNAME_IN_THE_CSV}
        """
        default_str = """    default_value: {DEFAULT}"""
        subtype_str = """    subtype: {SUBTYPE}"""
        trans_type = {
            ('integer', 'null'): 'int',
            ('number', 'null'): 'int',
            ('string',): 'string',
            'boolean': 'boolean',
            'integer': 'int',
            'number': 'int',
            'string': 'string'
            }
        default_value = []
        for key in self._get_dict_for_yaml().keys():
            if key.startswith('default_'):
                default_value.append(key[8:])
        if default_value:
            enum_dict = {k: self._get_dict_for_yaml()['default_' + k] for k in default_value}
        else: enum_dict = {}
        for key, value in self._get_dict_for_yaml().items():
            if not key.startswith('default_'):
                if enum_dict.get(key):
                    temp_d_str = temp_str + default_str
                    yaml_str += temp_d_str.format(
                        FIELDNAME_IN_THE_NODE=key,
                        TYPE="string",
                        FIELDNAME_IN_THE_CSV=value,
                        DEFAULT=enum_dict[key]
                    )
                elif key == 'type':
                    temp_d_str = temp_str + default_str
                    yaml_str += temp_d_str.format(
                        FIELDNAME_IN_THE_NODE=key,
                        TYPE="string",
                        FIELDNAME_IN_THE_CSV=value,
                        DEFAULT=snode
                    )
                else:
                    if get_type(nodeprops[key]) == 'list':
                        temp_d_str = temp_str + subtype_str
                        yaml_str += temp_d_str.format(
                            FIELDNAME_IN_THE_NODE=key,
                            TYPE='list',
                            FIELDNAME_IN_THE_CSV=value,
                            SUBTYPE='dict'
                        )
                    else:
                        yaml_str += temp_str.format(
                            FIELDNAME_IN_THE_NODE=key,
                            TYPE=trans_type.get(get_type(nodeprops[key])),
                            FIELDNAME_IN_THE_CSV=value
                        )
        return yaml_str

    def get_yaml_with_style(self, yaml_str, nodeprops, snode):
        '''get yaml with style'''
        yaml_style = yaml.dump(yaml.load(self.get_yaml_string(yaml_str, nodeprops, snode)), \
                     Dumper=MyDumper, indent=4, default_flow_style=False)
        return yaml_style
