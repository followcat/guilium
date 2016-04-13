import engine.matas.dom
import engine.matas.image
import engine.connector._mobile
import engine.connector._desktop


class Engine(object):
    connector_classes = {
        'mobile':   engine.connector._mobile.MobileConnector,
        'desktop':  engine.connector._desktop.DesktopConnector,
    }

    mata_classes = {
        'mobile':   {
            'image': engine.matas.image.WebviewImageMata,
            'dom':   engine.matas.dom.WebviewDomMata},
        'desktop':  {
            'image': engine.matas.image.DesktopImageMata,
            'dom':   engine.matas.dom.DesktopDomMata}
    }

    def __init__(self, name, config):
        self.name = name
        self.platform = config['platform']
        self.comm = self.connector_factory()
        self.matas = self.mata_factory()

    def mata_factory(self):
        return [_cls(_type) for _type, _cls in \
                    self.mata_classes[self.platform].items()]

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
            results[mata.type] = result
        return results


