import checkmate.checkmate.core.application


class Application(checkmate.checkmate.core.application.Application):
    """"""
    def __init__(self, suts, stub):
        self.components = {}
        for sut in suts:
            self.components[sut.name] = sut
        self.components['stub'] = stub

    def start(self):
        """"""
        for _c in self.components.values():
            _c.start()
