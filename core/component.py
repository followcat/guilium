import checkmate.checkmate.core.component


class Component(checkmate.checkmate.core.component.Component):
    """"""
    def __init__(self, name, engine):
        """"""
        checkmate.checkmate.core.component.Component.__init__(self, name, engine)
        self.stack = {}

    def start(self):
        """"""
        for e in self.engine:
            e.start()

    def process(self, url):
        """"""
        results = []
        for e in self.engine:
            result = e.process(url)
            results.append(result)
        self.stack[url] = results

    def get(self):
        return self.stack
