import math

import engine.matas.base
from engine.processor.image import webviewfullscreen, fullimage
from engine.processor.image import get_contain, get_webview, location, bounds, size


class WebviewImageMata(engine.matas.base.BaseMata):
    def shotfunc(self, driver):
        driver.switch_to.context('NATIVE_APP')
        png = driver.get_screenshot_as_png()
        driver.switch_to.context('CHROMIUM')
        return png

    def process(self, url, driver):
        driver.switch_to.context('CHROMIUM')
        driver.get(url)

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
        screenshots, last_moved = webviewfullscreen(driver, scroll_height,
                                                    self.shotfunc, scale)
        fullscreen = fullimage(screenshots,
                               webview_location['x'], webview_location['y'],
                               contain_size['width'], contain_size['height'],
                               last_moved)
        return fullscreen


