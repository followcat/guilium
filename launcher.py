import json
import time 

import engine.base
import core.storage
import core.component
import core.application
import core.communication
import validator.dom
import validator.image
import reportor.image


class Runtime(object):
    """"""
    def __init__(self, config_file):
        self.suts = {}
        self.stub = None
        try:
            self.config = json.load(open(config_file))
        except ValueError:
            config_content = open(config_file).read()
            self.config = json.loads(config_content.replace('\\', '\\\\'))
        self.storage = core.storage.Storage()
        self.validate_results = core.storage.Storage()
        self.communication_cls = core.communication.Communication
        self.setup_environment()
        self.validator = [validator.dom.DomValidator()]

    def setup_environment(self):
        for sut in self.config['sut']:
            name = sut['name']
            sut_engine = engine.base.Engine(name=name, config=sut)
            self.suts[name] = core.component.Component(name, sut_engine)
        stub = self.config['stub']
        stub_engine = \
            engine.base.Engine(name=stub['name'], config=stub)
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
        for validator in self.validator:
            results = validator.validate(test.test_url, self.storage,
                                         self.suts.values(), self.stub)
            self.validate_results.set(test.test_url, results)
        self.imagereport(test.test_url, self.stub)

    def imagereport(self, test_url, stub):
        stub_name = self.stub.name
        tests_results = self.validate_results.get()
        for sut_name in tests_results[test_url]:
            result = tests_results[test_url][sut_name]
            reportor.image.report(result, self.storage,
                                   sut_name, stub_name, test_url)

    def imagereportall(self):
        stub_name = self.stub.name
        tests_results = self.validate_results.get()
        for test_url in tests_results:
            for sut_name in tests_results[test_url]:
                result = tests_results[test_url][sut_name]
                reportor.image.report(result, self.storage,
                                       sut_name, stub_name, test_url)

