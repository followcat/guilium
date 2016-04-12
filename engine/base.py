import engine.matas.dom
import engine.matas.image
import engine.communication.base
import engine.communication._webdriver


class Engine(object):
    def __init__(self, name):
        self.comm = engine.communication._webdriver.Communication(name)
        self.matas = [engine.matas.image.ImageMata(),
                      engine.matas.dom.DomMata()]

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


