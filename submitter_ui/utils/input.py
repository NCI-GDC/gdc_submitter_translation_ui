# pylint: disable=C0325

'''input utils'''

import itertools
import requests as rq

def file_extention(filename):
    '''check ext'''
    return '.' in filename and filename.rsplit('.', 1)[1].lower()

def filter_list(alist, blist):
    '''remove blist from alist'''
    return list(set(alist)-set(blist))

class QueryAPI(object):
    '''this class describes some interactions with the GDC submission API,
    submission template, and GDC dictionary.
    '''
    def __init__(self, api, template):
        self.api = api
        self.template = template

    def get_all_node(self):
        '''get all node type from GDC dictionary
        '''
        node_list = []
        all_node_url = self.template + '?format=json'
        try:
            node_dict = rq.get(all_node_url).json()
            for dct in node_dict:
                node_list.append(dct.get('type'))
            node_list.sort()
        except rq.exceptions.ConnectionError as err:
            print('Failed to connect {}. {}'.format(all_node_url, err))
        return node_list

    def get_node_json(self, node):
        '''get node json'''
        node_url = self.api + str(node)
        node_json = rq.get(node_url).json()
        return node_json

    def get_enum(self, node):
        '''get enum of a property'''
        node_enum_dict = {}
        ndict = self.get_node_json(node)['properties']
        for prop in ndict.keys():
            enum = ndict[prop].get('enum')
            node_enum_dict[prop] = enum
        no_empty_dict = {k: v for k, v in node_enum_dict.items() if v is not None}
        return no_empty_dict

    def get_fields(self, node):
        '''check template, and group properties into 5 groups'''
        field_dict = {
            "required": [],
            "optional": [],
            "exclusive_links": [],
            "inexclusive_links": [],
            "links": [],
            "enums": {}
        }
        field_dict['enums'] = self.get_enum(node)
        if self.get_node_json(node).get('required'):
            rqlist = self.get_node_json(node)['required']
        else: rqlist = []
        stemp = '{}{}?format=json'.format(self.template, str(node))
        tplist = list(rq.get(stemp).json().keys())
        oplist = filter_list(tplist, rqlist)
        if self.get_node_json(node).get('links'):
            for link in self.get_node_json(node)['links']:
                if link.get('exclusive'):
                    field_dict['exclusive_links'].append([d['name'] for d in link['subgroup']])
                elif link.get('subgroup'):
                    for dct in link['subgroup']:
                        field_dict['inexclusive_links'].append(dct['name'])
                else:
                    field_dict['links'].append(link['name'])
        if field_dict.get('exclusive_links'):
            exclude_list = list(itertools.chain\
                           .from_iterable(field_dict['links'] + \
                           field_dict['exclusive_links'] + \
                           field_dict['inexclusive_links']))
        else:
            exclude_list = list(itertools.chain\
                           .from_iterable([field_dict['links'] + \
                           field_dict['exclusive_links'] + \
                           field_dict['inexclusive_links']]))
        field_dict['optional'] = filter_list(oplist, exclude_list) + ['s3_loc']
        field_dict['required'] = filter_list([x for x in rqlist if x in tplist], exclude_list)
        return field_dict

    def get_nodes_dict(self, node_list):
        '''get dict for all the selected nodes'''
        nodes_dict = {}
        for node in node_list:
            nodes_dict[node] = self.get_fields(node)
        return nodes_dict
