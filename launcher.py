import json
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
    def __init__(self, config_file):
        self.config = json.load(open(config_file))
        self.suts = {}
        self.stub = None
        self.storage = core.storage.Storage()
        self.communication_cls = core.communication.Communication
        self.setup_environment()
        self.validators = [validators.image.ImageValidator('WebviewImageMata'),
                           validators.dom.DomValidator('WebviewDomMata')]

    def setup_environment(self):
        for sut in self.config['sut']:
            name = sut['name']
            sut_engine = engine.base.Engine(name=name, config=sut['engine'])
            self.suts[name] = core.component.Component(name, sut_engine)
        stub = self.config['stub']
        stub_engine = \
            engine.base.Engine(name=stub['name'], config=stub['engine'])
        self.stub = core.component.Component(stub['name'], stub_engine)
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
