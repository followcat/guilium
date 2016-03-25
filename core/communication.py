import time
import threading

import checkmate.checkmate.core.communication


class Communication(checkmate.checkmate.core.communication.Communication, threading.Thread):
    """"""
    def __init__(self, suts, stub, storage):
        threading.Thread.__init__(self)
        checkmate.checkmate.core.communication.Communication.__init__(self)
        self.suts = suts
        self.stub = stub
        self.storage = storage
        self.stopcondition = False

    def start(self):
        threading.Thread.start(self)

    def run(self):
        while True:
            if self.stopcondition:
                break
            for name, sut in self.suts.items():
                info = sut.get()
                self.storage.set(name, info)
            time.sleep(0.01)

    def stop(self):
        self.stopcondition = True
