import json

import collections

import validators.base
import engine.matas.image


class DomValidator(validators.base.BaseValidator):

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
                driver.execute_script(one_label+"\none_label("+top+", "+left+", "+height+", "+width+");")
            except Exception as e:
                continue

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
                            d1[each][index]['height'] != d2[each][index]['height'] or
                            d1[each][index]['textContent'] != d2[each][index]['textContent']):
                            results.append(node_details(d1, each, index))
                            break
                        for s in d1[each][index]['style']:
                            if d1[each][index]['style'][s] != d2[each][index]['style'][s]:
                                results.append(node_details(d1, each, index))
                                break
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
            with open('/tmp/'+url.replace(":", "").replace("/", "")+'_'+sut.name+'.json', 'w') as fp:
                json.dump(results, fp)
            driver = sut.engine.comm.driver
            self.markelements(driver, results)
            tmp_img_matas = engine.matas.image.DesktopImageMata()
            indexModShot = tmp_img_matas.onlyshot(driver)
            indexModShot.save('/tmp/'+url.replace(":", "").replace("/", "")+'_'+sut.name+'.png')
