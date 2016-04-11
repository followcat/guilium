import time 

import engine.base
import core.storage
import core.component
import core.application
import core.communication
import validators.dom
import validators.image


class Runtime(object):
    """"""
    def __init__(self, config):
        self.config = config
        self.suts = {}
        self.stub = None
        self.storage = core.storage.Storage()
        self.communication_cls = core.communication.Communication
        self.setup_environment()
        self.validators = [validators.image.ImageValidator('ImageMata'),
                           validators.dom.DomValidator('DomMata')]

    def setup_environment(self):
        for sut in self.config.sut:
            sut_engine = engine.base.Engine(name=sut)
            self.suts[sut] = core.component.Component(sut, sut_engine)
        stub_engine = engine.base.Engine(name=self.config.stub)
        self.stub = core.component.Component(self.config.stub, stub_engine)
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

    def execute(self, test):
        stack = self.storage.get()
        for component in [self.stub] + self.suts.values():
            component.push(test.test_url)
        while True:
            time.sleep(0.1)
            for component in [self.stub] + self.suts.values():
                if component.name in stack and \
                    test.test_url in stack[component.name]:
                    continue
                else:
                    break
            else:
                break
        for validator in self.validators:
            validator.validate(test.test_url, self.storage,
                self.suts.values(), self.stub)
