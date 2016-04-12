import engine.matas.dom
import engine.matas.image
import engine.connector._mobile
import engine.connector._desktop


class Engine(object):
    connector_classes = {
        'mobile':   engine.connector._mobile.MobileConnector,
        'desktop':  engine.connector._desktop.DesktopConnector,
    }

    def __init__(self, name, config):
        self.name = name
        self.platform = config['platform']
        self.comm = self.connector_factory()
        self.matas = [engine.matas.image.WebviewImageMata(),
                      engine.matas.dom.WebviewDomMata()]

    def connector_factory(self):
        return self.connector_classes[self.platform](self.name)

    def start(self):
        self.comm.start()

    def stop(self):
        self.comm.stop()

    def process(self, url):
        results = {}
        for mata in self.matas:
            result = mata.process(url, self.comm.driver)
            results[mata.name] = result
        return results


