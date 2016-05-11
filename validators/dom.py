import json
import difflib
import hashlib
import collections

import Image

import validators.base
import validators.error
import engine.matas.image


class DomValidator(validators.base.BaseValidator):

    def __init__(self, compare_text=False):
        super(DomValidator, self).__init__()
        self.compare_text = compare_text

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

        def node_details(node, node2=None, extra=False):
            if node2 is not None:
                diffs = {'top': node['top']-node2['top'],
                         'left': node['left']-node2['left'],
                         'height': node['height']-node2['height'],
                         'width': node['width']-node2['width'],
                         'text': node['innerText']}
                return (node['top'], node['left'], node['height'], node['width'], extra, diffs)
            return (node['top'], node['left'], node['height'], node['width'], extra)

        def compare_node(node1, node2):
            try:
                if ((not fuzzy_equals(node1['top'], node2['top']+offsets['top'])) and \
                        (not fuzzy_equals(node1['top'], node2['top'])) or
                    not fuzzy_equals(node1['left'], node2['left']) or
                    not fuzzy_equals(node1['width'], node2['width']) or
                    not fuzzy_equals(node1['height'], node2['height'])):
                    results.append(node_details(node1, node2))
                    if node1['top'] != node2['top']:
                        offsets['top'] = node1['top'] - node2['top']
                    else:
                        offsets['top'] = 0
                    return
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
                             '--' + str(_e['id']) + \
                             '--' + str(_e['parentNode'])
                md5_list.append(hashlib.md5(id_str).hexdigest())
            return md5_list

        sd = difflib.SequenceMatcher(None, node_list_md5s(d1), node_list_md5s(d2))
        blocks = sd.get_matching_blocks()
        last_stop_index_1 = 0
        last_stop_index_2 = 0
        for _b in blocks:
            for _i in range(last_stop_index_1, _b.a):
                results.append(node_details(d1[_i]))
            for _i in range(last_stop_index_2, _b.b):
                results.append(node_details(d2[_i], extra=True))
            for index in range(_b.size):
                compare_node(d1[_b.a+index], d2[_b.b+index])
            last_stop_index_1 = _b.a + _b.size
            last_stop_index_2 = _b.b + _b.size
        return results

    def validate(self, url, storage, suts, stub):
        stack = storage.get()
        stub_dom = stack[stub.name][url][self.type]
        stub_info = self.nodefilter(stub_dom)
        for sut in suts:
            sut_dom = stack[sut.name][url][self.type]
            sut_info = self.nodefilter(sut_dom)
            results = self.nodecomparer(stub_info, sut_info)
            driver = sut.engine.comm.driver
            self.markelements(driver, results)
            image_file = self.imagereport(results, sut, stub, url)
            if len(results) > 0:
                json_file = '/tmp/'+url.replace(":", "").replace("/", "")+'_'+sut.name+'.json'
                with open(json_file, 'w') as fp:
                    json.dump(results, fp)
                json_link = 'file://' + json_file
                image_link = 'file://' + image_file
                raise validators.error.TestError("%d differences found in "
                            "positions %s... "
                            "\nSee %s"
                            "\n %s"%(len(results), results[0][0], json_link, image_link))

    def markelements(self, driver, results):
        one_label = """
        function one_label(top, left, height, width, color) {
            d = document.createElement("div");
            d.style.position="absolute";
            d.style.top=top+"px";
            d.style.left=left+"px";
            d.style.width=width+"px";
            d.style.height=height+"px";
            d.style.border="2px dashed "+color;
            document.body.appendChild(d);
            return d;
        }
        """
        all_labels = ""
        for each in results:
            top = str(each[0])
            left = str(each[1])
            height = str(each[2])
            width = str(each[3])
            if each[4]:
                all_labels += "\none_label("+top+", "+left+", "+height+", "+width+", 'green');"
            else:
                all_labels += "\none_label("+top+", "+left+", "+height+", "+width+", 'red');"
        driver.execute_script(one_label+all_labels)

    def imagereport(self, differences, sut, stub, url):
        sut_driver = sut.engine.comm.driver
        stub_driver = stub.engine.comm.driver

        self.markelements(sut_driver, differences)
        if sut.engine.platform == 'mobile':
            sut_img_mata = engine.matas.image.WebviewImageMata()
        elif sut.engine.platform == 'desktop':
            sut_img_mata = engine.matas.image.DesktopImageMata()
        sut_img_mata.loaddriver(sut_driver)
        sutShot = sut_img_mata.screenshot()

        if stub.engine.platform == 'mobile':
            stub_img_mata = engine.matas.image.WebviewImageMata()
        elif stub.engine.platform == 'desktop':
            stub_img_mata = engine.matas.image.DesktopImageMata()
        stub_img_mata.loaddriver(stub_driver)
        stubShot = stub_img_mata.screenshot()

        sut_width, sut_height = sutShot.size
        stub_width, stub_height = stubShot.size
        if stub_width > sut_width:
            scale = float(sut_width)/float(stub_width)
            stubShot = stubShot.resize((sut_width, int(stub_height*scale)))
            stub_width, stub_height = stubShot.size
        elif stub_width < sut_width:
            scale = float(stub_width)/float(sut_width)
            sutShot = sutShot.resize((stub_width, int(sut_height*scale)))
            sut_width, sut_height = sutShot.size
        result_image = Image.new('RGBA', (sut_width+stub_width,
                                          max(sut_height, stub_height)))
        result_image.paste(sutShot, (0, 0))
        result_image.paste(stubShot, (sut_width, 0))
        img_file = '/tmp/'+url.replace(":", "").replace("/", "")+'_'+sut.name+'.png'
        result_image.save(img_file)
        if len(differences) > 0:
            init_y1 = differences[0][0]
            init_y2 = differences[0][0] + differences[0][2]
            for _index, diff in enumerate(differences):
                if diff[0] < init_y1 or diff[2] > 400 or diff[2] == 0:
                    continue
                if diff[0] < init_y1:
                    init_y1 = diff[0]
                if diff[0] > init_y2 +100:
                    img_piece = result_image.crop((0, init_y1-20,
                                    result_image.size[0], init_y2+20))
                    img_piece.save('/tmp/diff/image_piece_%s.png'
                                    %str((0, init_y1)))
                    init_y1 = diff[0]
                if diff[0] + diff[2] > init_y2:
                    init_y2 = diff[0] + diff[2]
            img_piece = result_image.crop((0, init_y1-20,
                            result_image.size[0], init_y2+20))
            img_piece.save('/tmp/diff/image_piece_%s.png'%str((0, init_y1)))
        return img_file
