import re
import time
import math
import StringIO
import xml.etree.ElementTree as ET

import Image

import engines.base


def bounds(points_str):
    """
        >>> import engines.image
        >>> engines.image.bounds('[0,0][480,800]')
        [0, 0, 480, 800]
    """
    return [int(each) for each in re.findall(r'[\d]+', points_str)]


def size(bound):
    """
        >>> import engines.image
        >>> bound = [0, 0, 480, 800]
        >>> size = engines.image.size(bound)
        >>> size['width'], size['height']
        (480, 800)
    """
    return {'width':bound[2]-bound[0], 'height':bound[3]-bound[1]} 


def location(bound):
    """
        >>> import engines.image
        >>> bound = [0, 0, 480, 800]
        >>> location = engines.image.location(bound)
        >>> location['x'], location['y']
        (0, 0)
    """
    return {'x':bound[0], 'y':bound[1]}


class ImageEngine(engines.base.BaseEngine):

    def get_contain(self):
        self.driver.switch_to.context('NATIVE_APP')
        xmlsrc = self.driver.page_source
        xmlobj = ET.fromstring(xmlsrc.encode('utf-8'))[0]
        return xmlobj

    def get_webview(self):
        """"""
        def area(elem):
            bound = bounds(elem.get('bounds'))
            return (bound[2]-bound[0])*(bound[3]-bound[1])
        def allview(xmlobj, save=None):
            if save is None:
                save = []
            elems = list(xmlobj)
            for each in elems:
                allview(each, save)
            if xmlobj.tag == 'android.view.View':
                save.append(xmlobj)
            return save
        self.driver.switch_to.context('NATIVE_APP')
        xmlsrc = self.driver.page_source
        xmlobj = ET.fromstring(xmlsrc.encode('utf-8'))
        results = sorted(allview(xmlobj), key=lambda each: area(each), reverse=True)
        return results[0]

    def webviewfullscreen(self):
        """"""
        cimgs = []
        screenshots = []
        self.driver.switch_to.context('CHROMIUM')
        self.driver.execute_script('window.scrollTo(0, 0);')
        time.sleep(1)

        contain = self.get_contain()
        contain_bound = bounds(contain.get('bounds'))
        contain_size = size(contain_bound)
        webview = self.get_webview()
        webview_bound = bounds(webview.get('bounds'))
        webview_location = location(webview_bound)

        self.driver.switch_to.context('CHROMIUM')
        total_hegiht = self.driver.execute_script('return document.body.scrollHeight')
        screen_height = self.driver.execute_script('return window.screen.height')

        scale = float(screen_height)/contain_size['height']
        scroll_height = math.ceil((contain_size['height']-webview_location['y'])*scale)
        moved = 0
        count = 0
        while True:
            last_moved = moved
            self.driver.switch_to.context('CHROMIUM')
            scrolled = self.driver.execute_script('return document.body.scrollTop')
            self.driver.execute_script('window.scrollTo(0, %d);' % (count*scroll_height))
            moved = self.driver.execute_script('return document.body.scrollTop') - scrolled
            time.sleep(1)
            self.driver.switch_to.context('NATIVE_APP')
            png = self.driver.get_screenshot_as_png()
            screenshots.append(png)
            count += 1
            if count == 2:
                break
            if last_moved > moved or (last_moved > 0 and moved == 0):
                break
        the_last_moved = int(moved/scale)

        for each in range(len(screenshots)):
            img = Image.open(StringIO.StringIO(screenshots[each]))
            region = [webview_location['x'], webview_location['y'],
                      contain_size['width'], contain_size['height']]
            if each == len(screenshots)-1:
                region[1]=region[3]-the_last_moved
            cimg = img.crop(tuple(region))
            cimgs.append(cimg)

        image_height = sum([each.size[1] for each in cimgs])
        result_image = Image.new('RGBA', (contain_size['width'], image_height))
        paste_height = 0
        for each in cimgs:
            result_image.paste(each, (0, paste_height))
            paste_height += each.size[1]
        return result_image

    def process(self, url):
        self.driver.switch_to.context('CHROMIUM')
        self.driver.get(url)
        image = self.webviewfullscreen()
        return image