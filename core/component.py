import checkmate.checkmate.core.component


class Component(checkmate.checkmate.core.component.Component):
    """"""

    def start(self):
        """"""
        for e in self.engine:
            e.start()

    def process(self, url):
        """"""
        for e in self.engine:
            e.process(url)
