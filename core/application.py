import checkmate.checkmate.core.application


class Application(checkmate.checkmate.core.application.Application):
    """"""
    def __init__(self, suts, stub):
        self.components = {}
        self.sut = {}
        for sut in suts:
            self.components[sut.name] = sut
            self.sut[sut.name] = sut
        self.components[stub.name] = stub
        self.stub = stub

    def start(self):
        """"""
        for _c in self.components.values():
            _c.start()
