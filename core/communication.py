import time
import threading

import checkmate.checkmate.core.communication


class Communication(checkmate.checkmate.core.communication.Communication, threading.Thread):
    """"""
    def __init__(self, suts, stub, storage):
        checkmate.checkmate.core.communication.Communication.__init__(self)
        threading.Thread.__init__(self)
        self.suts = suts
        self.stub = stub
        self.storage = storage

    def run(self):
        while True:
            for name in suts:
                sut = suts[name]
                info = sut.get()
                self.storage.set(sut.name, info)
                time.sleep(0.001)

    def simulate(self, url):
        self.stub.process(url)
        info = self.stub.get()
        self.storage.set(self.stub.name, info)
        for name in self.suts:
            sut = self.suts[name]
            sut.process(url)

