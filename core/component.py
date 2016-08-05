import time
import threading

import checkmate.core.component


class Component(checkmate.core.component.Component, threading.Thread):
    """"""
    def __init__(self, name, engine):
        """"""
        threading.Thread.__init__(self)
        checkmate.core.component.Component.__init__(self, name, engine)
        self.jobs = []
        self.stack = {}
        self.stopcondition = False

    def start(self):
        """"""
        self.engine.start()
        threading.Thread.start(self)

    def run(self):
        while True:
            if self.stopcondition:
                break
            time.sleep(0.01)
            if not self.jobs:
                continue
            job = self.jobs.pop()
            self.process(job)

    def push(self, url):
        self.jobs.append(url)

    def process(self, url):
        """"""
        results = self.engine.process(url)
        self.stack[url] = results

    def get(self):
        return self.stack

    def stop(self):
        if self.is_alive():
            self.stopcondition = True
            self.engine.stop()
