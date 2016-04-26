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
        screen_height = self.driver.execute_script('return window.screen.height')
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
        screenshots, last_moved = webviewfullscreen(self.driver, self.SCROLLHEIGHT,
                                                    self.shotfunc, self.SCALE)
        fullscreen = fullimage(screenshots, self.X, self.Y,
                               self.WIDTH, self.HEIGHT,
                               last_moved)
        return fullscreen

class WebviewImageMata(ImageMata):

    @property
    def SCROLLHEIGHT(self):
        scroll_height = math.ceil((self.HEIGHT-self.Y)*self.SCALE)
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
        return self.contain_size['height']

    @property
    def SCALE(self):
        self.driver.switch_to.context('CHROMIUM')
        screen_height = self.driver.execute_script('return window.screen.height')
        return float(screen_height)/self.HEIGHT

    def shotfunc(self):
        self.driver.switch_to.context('NATIVE_APP')
        png = self.driver.get_screenshot_as_png()
        self.driver.switch_to.context('CHROMIUM')
        return png

    def loaddriver(self, driver):
        self.driver = driver
        contain = get_contain(driver)
        contain_bound = bounds(contain.get('bounds'))
        self.contain_size = size(contain_bound)
        webview = get_webview(driver)
        webview_bound = bounds(webview.get('bounds'))
        self.webview_location = location(webview_bound)

    def process(self, url, driver):
        self.loaddriver(driver)
        self.driver.switch_to.context('CHROMIUM')
        self.driver.get(url)
        fullscreen = self.screenshot()
        return fullscreen


class DesktopImageMata(ImageMata):

    def process(self, url, driver):
        self.loaddriver(driver)
        self.driver.get(url)
        fullscreen = self.screenshot()
        return fullscreen
