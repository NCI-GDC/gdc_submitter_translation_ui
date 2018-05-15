# pylint: disable=R0901
'''output utils'''

import yaml

class MyDumper(yaml.Dumper):
    """
    customize indent dumper
    """
    def increase_indent(self, flow=False, indentless=False):
        return super(MyDumper, self).increase_indent(flow, False)
