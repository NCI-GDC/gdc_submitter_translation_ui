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

    def get_fields(self, node):
        '''check template, and group properties into 3 groups'''
        if self.get_node_json(node).get('required'):
            rqlist = self.get_node_json(node)['required']
        else: rqlist = []
        stemp = '{}{}?format=json'.format(self.template, str(node))
        tplist = list(rq.get(stemp).json().keys())
        oplist = filter_list(tplist, rqlist)
        links = []
        exclusive_links = []
        inexclusive_links = []
        if self.get_node_json(node).get('links'):
            for link in self.get_node_json(node)['links']:
                if link.get('exclusive'):
                    exclusive_links.append([d['name'] for d in link['subgroup']])
                elif link.get('subgroup'):
                    for dct in link['subgroup']:
                        inexclusive_links.append(dct['name'])
                else:
                    links.append(link['name'])
        if exclusive_links:
            exclude_list = list(itertools.chain\
                           .from_iterable(links + exclusive_links + inexclusive_links))
        else:
            exclude_list = list(itertools.chain\
                           .from_iterable([links + exclusive_links + inexclusive_links]))
        optional = filter_list(oplist, exclude_list) + ['s3_loc']
        required = filter_list([x for x in rqlist if x in tplist], exclude_list)
        return required, optional, exclusive_links, inexclusive_links, links

    def get_enum(self, node):
        '''get enum of a property'''
        node_enum_dict = {}
        nurl = self.api + str(node)
        ndict = rq.get(nurl).json()['properties']
        for prop in ndict.keys():
            enum = ndict[prop].get('enum')
            node_enum_dict[prop] = enum
        no_empty_dict = {k: v for k, v in node_enum_dict.items() if v is not None}
        return no_empty_dict
