import engine.communication.base
import engine.matas.image


class Engine(object):
    def __init__(self, name):
        self.comm = engine.communication.base.Communication(name)
        self.maytas = [engine.matas.image.ImageEngine(name)]

    def start(self):
        self.comm.start()

    def stop(self):
        self.comm.stop()

    def process(self, url):
        results = []
        for each in self.maytas:
            result = each.process(url, self.comm.driver)
            results.append(result)
        return results


