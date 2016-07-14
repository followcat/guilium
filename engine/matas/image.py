import math

import engine.matas.base
from engine.processor.image import webviewfullscreen, fullimage
from engine.processor.image import get_contain, get_webview, location, bounds, size


class ImageMata(engine.matas.base.BaseMata):

    @property
    def WIDTH(self):
        screen_width = self.driver.execute_script('return window.screen.width')
        return screen_width

    @property
    def HEIGHT(self):
        if 'device name' in self.config:
            height_js = "return window.screen.height"
        else:
            height_js = """
                var e = window;
                var a = 'inner';
                if (!('innerWidth' in window )){
                    a = 'client';
                    e = document.documentElement || document.body;
                }
                return e[ a+'Height' ];
            """
        screen_height = self.driver.execute_script(height_js)
        return screen_height

    @property
    def SCROLLHEIGHT(self):
        scroll_height = int(self.HEIGHT)
        return scroll_height

    @property
    def X(self):
        return 0

    @property
    def Y(self):
        return 0

    @property
    def SCALE(self):
        return 1

    def loaddriver(self, driver):
        self.driver = driver

    def shotfunc(self):
        png = self.driver.get_screenshot_as_png()
        return png

    def screenshot(self):
        if self.driver.name in ['IE', 'Internet Explorer', 'ie', 'internet explorer'] or \
            self.driver.name in ['Firefox', 'firefox', 'ff', 'FF']:
            screenshots, last_moved = \
                webviewfullscreen(self.driver, self.SCROLLHEIGHT,
                                  self.shotfunc, self.SCALE, page_limit=1)
        else:
            screenshots, last_moved = \
                webviewfullscreen(self.driver, self.SCROLLHEIGHT,
                                  self.shotfunc, self.SCALE)
        fullscreen = fullimage(screenshots, self.X, self.Y,
                               self.WIDTH, self.HEIGHT,
                               last_moved)
        return fullscreen

class WebviewImageMata(ImageMata):

    @property
    def SCROLLHEIGHT(self):
        scroll_height = math.ceil(self.HEIGHT*self.SCALE)
        return scroll_height

    @property
    def X(self):
        return self.webview_location['x']

    @property
    def Y(self):
        return self.webview_location['y']

    @property
    def WIDTH(self):
        return self.contain_size['width']

    @property
    def HEIGHT(self):
        return self.contain_size['height'] - self.Y

    @property
    def SCALE(self):
        return float(self.screen_width)/self.contain_size['width']

    def shotfunc(self):
        self.driver.switch_to.context('NATIVE_APP')
        png = self.driver.get_screenshot_as_png()
        self.driver.switch_to.context('CHROMIUM')
        return png

    def loaddriver(self, driver):
        self.driver = driver
        self.driver.switch_to.context('NATIVE_APP')
        contain = get_contain(driver)
        contain_bound = bounds(contain.get('bounds'))
        self.contain_size = size(contain_bound)
        webview = get_webview(driver)
        webview_bound = bounds(webview.get('bounds'))
        self.webview_location = location(webview_bound)
        self.driver.switch_to.context('CHROMIUM')
        self.screen_width = self.driver.execute_script('return window.screen.width')

    def process(self, url, driver):
        self.loaddriver(driver)
        self.driver.switch_to.context('CHROMIUM')
        fullscreen = self.screenshot()
        return fullscreen


class DesktopImageMata(ImageMata):

    def process(self, url, driver):
        self.loaddriver(driver)
        fullscreen = self.screenshot()
        return fullscreen
