import engine.matas.dom
import engine.matas.image
import engine.connector._mobile
import engine.connector._desktop

from engine.processor.image import ignore_fixed_element, scrollfullscreen


class Engine(object):
    connector_classes = {
        'mobile':   engine.connector._mobile.MobileConnector,
        'desktop':  engine.connector._desktop.DesktopConnector,
    }

    mata_classes = {
        'mobile':   [engine.matas.dom.WebviewDomMata,
                     engine.matas.image.WebviewImageMata],
        'desktop':  [engine.matas.dom.DesktopDomMata,
                     engine.matas.image.DesktopImageMata]
    }

    def __init__(self, name, config):
        self.name = name
        self.config = config
        self.platform = config['platform']
        self.comm = self.connector_factory()
        self.matas = self.mata_factory()

    def mata_factory(self):
        return [_cls(self.config) for _cls in self.mata_classes[self.platform]]

    def connector_factory(self):
        return self.connector_classes[self.platform](self.config)

    def start(self):
        self.comm.start()

    def stop(self):
        self.comm.stop()

    def preprocess(self, ignore_fixed=False):
        scrollfullscreen(self.comm.driver)
        if ignore_fixed:
            ignore_fixed_element(self.comm.driver)

    def process(self, url):
        results = {}
        if isinstance(url, tuple):
            actions = url[1]
            actions(self.comm.driver)
        self.preprocess()
        for mata in self.matas:
            result = mata.process(url, self.comm.driver)
            results[mata.type] = result
        return results


