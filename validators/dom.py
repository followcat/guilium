import json
import collections

import Image

import validators.base
import validators.error
import engine.matas.image


class DomValidator(validators.base.BaseValidator):

    def __init__(self, compare_text=False):
        super(DomValidator, self).__init__()
        self.compare_text = compare_text

    def nodefilter(self, node, d=None):
        x = dict(node)
        x.pop('attributes')
        x.pop('childNodes')
        if d is None:
            d = collections.OrderedDict()
        if (x['top'], x['left']) not in d:
            d[(x['top'], x['left'])] = []
        d[(x['top'], x['left'])].append(x)
        for each in node['attributes']:
            self.nodefilter(each, d)
        for each in node['childNodes']:
            self.nodefilter(each, d)
        return d

    def nodecomparer(self, d1, d2):
        results = []

        def node_details(node, index_1, index_2):
            return (index_1, index_2, node[index_1][index_2]['height'],
                    node[index_1][index_2]['width'])

        for each in d1:
            if each == (None, None):
                continue
            for index in range(len(d1[each])):
                if each not in d2:
                    results.append(node_details(d1, each, index))
                    continue
                else:
                    try:
                        if (d1[each][index]['width'] != d2[each][index]['width'] or
                            d1[each][index]['height'] != d2[each][index]['height']):
                            results.append(node_details(d1, each, index))
                            break
                        for s in d1[each][index]['style']:
                            if d1[each][index]['style'][s] != d2[each][index]['style'][s]:
                                results.append(node_details(d1, each, index))
                                break
                        if self.compare_text and \
                            d1[each][index]['innerText'] != d2[each][index]['innerText']:
                            if d1[each][index]['nodename'] in ['STYLE', 'SCRIPT']:
                                continue
                            results.append(node_details(d1, each, index))
                    except IndexError:
                        results.append(node_details(d1, each, index))
                        continue
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
        function one_label(top, left, height, width) {
            d = document.createElement("div");
            d.style.position="absolute";
            d.style.top=top+"px";
            d.style.left=left+"px";
            d.style.width=width+"px";
            d.style.height=height+"px";
            d.style.border='2px dashed red';
            document.body.appendChild(d);
            return d;
        }
        """
        for each in results:
            top = str(each[0][0])
            left = str(each[0][1])
            height = str(each[2])
            width = str(each[3])
            try:
                driver.execute_script(one_label+"\none_label("+top+", "+left+","
                                      +height+", "+width+");")
            except Exception as e:
                continue

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
        return img_file
