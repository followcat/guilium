import re
import time
import math
import StringIO
import xml.etree.ElementTree as ET

import Image


def bounds(points_str):
    """
        >>> import screen_storage
        >>> screen_storage.bounds('[0,0][480,800]')
        [0, 0, 480, 800]
    """
    return [int(each) for each in re.findall(r'[\d]+', points_str)]


def size(bound):
    """
        >>> import screen_storage
        >>> bound = [0, 0, 480, 800]
        >>> size = screen_storage.size(bound)
        >>> size['width'], size['height']
        (480, 800)
    """
    return {'width':bound[2]-bound[0], 'height':bound[3]-bound[1]} 


def location(bound):
    """
        >>> import screen_storage
        >>> bound = [0, 0, 480, 800]
        >>> location = screen_storage.location(bound)
        >>> location['x'], location['y']
        (0, 0)
    """
    return {'x':bound[0], 'y':bound[1]}


def get_contain(driver):
    driver.switch_to.context('NATIVE_APP')
    xmlsrc = driver.page_source
    xmlobj = ET.fromstring(xmlsrc.encode('utf-8'))[0]
    return xmlobj


def get_webview(driver):
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
    driver.switch_to.context('NATIVE_APP')
    xmlsrc = driver.page_source
    xmlobj = ET.fromstring(xmlsrc.encode('utf-8'))
    results = sorted(allview(xmlobj), key=lambda each: area(each), reverse=True)
    return results[0]


def webviewfullscreen(driver):
    """"""
    cimgs = []
    screenshots = []
    driver.switch_to.context('CHROMIUM')
    driver.execute_script('window.scrollTo(0, 0);')
    time.sleep(1)

    contain = get_contain(driver)
    contain_bound = bounds(contain.get('bounds'))
    contain_size = size(contain_bound)
    webview = get_webview(driver)
    webview_bound = bounds(webview.get('bounds'))
    webview_location = location(webview_bound)

    driver.switch_to.context('CHROMIUM')
    total_hegiht = driver.execute_script('return document.body.scrollHeight')
    screen_height = driver.execute_script('return window.screen.height')

    scale = float(screen_height)/contain_size['height']
    scroll_height = math.ceil((contain_size['height']-webview_location['y'])*scale)
    moved = 0
    count = 0
    while True:
        last_moved = moved
        driver.switch_to.context('CHROMIUM')
        scrolled = driver.execute_script('return document.body.scrollTop')
        driver.execute_script('window.scrollTo(0, %d);' % (count*scroll_height))
        moved = driver.execute_script('return document.body.scrollTop') - scrolled
        time.sleep(1)
        driver.switch_to.context('NATIVE_APP')
        png = driver.get_screenshot_as_png()
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
