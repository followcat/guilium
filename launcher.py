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
        for sut in self.config.sut:
            sut_engines = [engines.baseengine.BaseEngine(name=sut)]
            suts.append(core.component.Component(sut, sut_engines))
        stub_engines = [engines.baseengine.BaseEngine(name=self.config.stub)]
        stub = core.component.Component(self.config.stub, stub_engines)
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
