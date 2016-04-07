import time
import threading

import checkmate.core.communication


class Communication(checkmate.core.communication.Communication, threading.Thread):
    """"""
    def __init__(self, suts, stub, storage):
        threading.Thread.__init__(self)
        checkmate.core.communication.Communication.__init__(self)
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
            for component in [self.stub] + self.suts.values():
                info = component.get()
                self.storage.set(component.name, info)
            time.sleep(0.01)

    def stop(self):
        self.stopcondition = True
