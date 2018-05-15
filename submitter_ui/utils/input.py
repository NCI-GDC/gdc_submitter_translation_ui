'''input utils'''

import requests as rq

def file_extention(filename):
    '''check ext'''
    return '.' in filename and filename.rsplit('.', 1)[1].lower()

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
        all_node_url = self.api + '_all'
        try:
            node_type = rq.get(all_node_url).json()
        except rq.exceptions.ConnectionError as err:
            print('Failed to connect {}. {}'.format(all_node_url, err))
        node_list = list(x for x in node_type.keys() if not x.startswith('_') and x != 'metaschema')
        return node_list

    def get_fields(self, node):
        '''check template, and group properties into 3 groups'''
        surl = self.api + str(node)
        sdict = rq.get(surl).json()
        rqlist = []
        if sdict.get('required'):
            rqlist = sdict['required']
        stemp = '{}{}?format=json'.format(self.template, str(node))
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
