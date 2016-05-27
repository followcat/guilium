import difflib
import hashlib

import validator.base
import validator.error


class DomValidator(validator.base.BaseValidator):

    def __init__(self, compare_text=False, compare_style=False):
        super(DomValidator, self).__init__()
        self.compare_text = compare_text
        self.compare_style = compare_style

    def nodefilter(self, node, l=None):
        x = dict(node)
        x.pop('attributes')
        x.pop('childNodes')
        if l is None:
            l = []
        for each in node['attributes']:
            self.nodefilter(each, l)
        for each in node['childNodes']:
            self.nodefilter(each, l)
        if x not in l:
            l.append(x)
        return l

    def nodecomparer(self, d1, d2):
        results = []
        offsets = {'top': 0}

        def fuzzy_equals(num1, num2, extra=5):
            if not isinstance(num1, int) or not isinstance(num2, int):
                return False
            return num2 in range(num1-extra, num1+extra+1)

        def node_details(node, node2=None, diff_type='unmatch'):
            if node2 is not None and diff_type == 'unmatch':
                diffs = {'top': node['top']-node2['top'],
                         'left': node['left']-node2['left'],
                         'height': node['height']-node2['height'],
                         'width': node['width']-node2['width'],
                         'text': node['innerText']}
                return (node['top'], node['left'], node['height'], node['width'], node['marginheight'], diff_type, diffs)
            return (node['top'], node['left'], node['height'], node['width'], node['marginheight'], diff_type)

        def compare_node(node1, node2):
            try:
                if ((not fuzzy_equals(node1['top'], node2['top']+offsets['top'])) and \
                        (not fuzzy_equals(node1['top'], node2['top'])) or
                    not fuzzy_equals(node1['left'], node2['left']) or
                    not fuzzy_equals(node1['width'], node2['width']) or
                    not fuzzy_equals(node1['height'], node2['height'])):
                    results.append(node_details(node1, node2, diff_type='unmatch'))
                    if node1['top'] != node2['top']:
                        offsets['top'] = node1['top'] - node2['top']
                    else:
                        offsets['top'] = 0
                    return
                if self.compare_style:
                    for s in node1['style']:
                        if node1['style'][s] != node2['style'][s]:
                            results.append(node_details(node1))
                            return
                if self.compare_text and \
                    node1['innerText'] != node2['innerText']:
                    if node1['nodename'] in ['STYLE', 'SCRIPT']:
                        return
                    results.append(node_details(node1))
            except IndexError:
                results.append(node_details(node1))
                return

        def node_list_md5s(node_list):
            md5_list = []
            for _e in node_list:
                id_str = str(_e['nodename']) + \
                             '--' + str(_e['class']) + \
                             '--' + str(_e['parentNode'])
                md5_list.append(hashlib.md5(id_str).hexdigest())
            return md5_list

        sd = difflib.SequenceMatcher(None, node_list_md5s(d1), node_list_md5s(d2))
        blocks = sd.get_matching_blocks()
        last_stop_index_1 = 0
        last_stop_index_2 = 0
        for _b in blocks:
            for _i in range(last_stop_index_1, _b.a):
                results.append(node_details(d1[_i], diff_type='miss'))
            for _i in range(last_stop_index_2, _b.b):
                results.append(node_details(d2[_i], diff_type='extra'))
            for index in range(_b.size):
                compare_node(d1[_b.a+index], d2[_b.b+index])
            last_stop_index_1 = _b.a + _b.size
            last_stop_index_2 = _b.b + _b.size
        return results

    def validate(self, url, storage, suts, stub):
        results = {}
        stack = storage.get()
        stub_dom = stack[stub.name][url][self.type]
        stub_info = self.nodefilter(stub_dom)
        for sut in suts:
            sut_dom = stack[sut.name][url][self.type]
            sut_info = self.nodefilter(sut_dom)
            results[sut.name] = self.nodecomparer(stub_info, sut_info)
        return results
