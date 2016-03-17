import core.component
import core.application
import core.communication



class Runtime(object):
    """"""
    def __init__(self, config):
        self.config = config
        self.communication = core.communication.Communication
        self.setup_environment()

    def setup_environment(self):
        suts = []
        import engines.baseengine
        engines = [engines.baseengine.BaseEngine]
        for sut in self.config.sut:
            suts.append(core.component.Component(sut, engines))
        stub = core.component.Component(self.config.stub, engines)
        self.application = core.application.Application(suts, stub)

    def start_test(self):
        self.application.start()
