import core.storage
import core.component
import core.application
import core.communication
import validators.imagediff


class Runtime(object):
    """"""
    def __init__(self, config):
        self.config = config
        self.storage = core.storage.Storage()
        self.communication_cls = core.communication.Communication
        self.setup_environment()
        self.validators = [validators.imagediff.ImageDiff()]

    def setup_environment(self):
        suts = []
        import engines.baseengine
        engines = [engines.baseengine.BaseEngine]
        for sut in self.config.sut:
            suts.append(core.component.Component(sut, engines))
        stub = core.component.Component(self.config.stub, engines)
        self.application = core.application.Application(suts, stub)
        self.communication = self.communication_cls(self.application.sut,
                                                    self.application.stub,
                                                    self.storage)

    def start_test(self):
        self.application.start()
        self.communication.start()

    def stop_test(self):
        self.application.stop()
        self.communication.stop()
