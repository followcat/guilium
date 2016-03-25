import core.storage
import core.component
import core.application
import core.communication
import validators.imagediff


class Runtime(object):
    """"""
    def __init__(self, config):
        self.config = config
        self.suts = {}
        self.stub = None
        self.storage = core.storage.Storage()
        self.communication_cls = core.communication.Communication
        self.setup_environment()
        self.validators = [validators.imagediff.ImageDiff()]

    def setup_environment(self):
        import engines.baseengine
        for sut in self.config.sut:
            sut_engines = [engines.baseengine.BaseEngine(name=sut)]
            self.suts[sut] = core.component.Component(sut, sut_engines)
        stub_engines = [engines.baseengine.BaseEngine(name=self.config.stub)]
        self.stub = core.component.Component(self.config.stub, stub_engines)
        self.communication = \
            self.communication_cls(self.suts, self.stub, self.storage)

    def start_test(self):
        for sut in self.suts.values():
            sut.start()
        self.stub.start()
        self.communication.start()

    def stop_test(self):
        self.stub.stop()
        for sut in self.suts.values():
            sut.stop()
        self.communication.stop()
