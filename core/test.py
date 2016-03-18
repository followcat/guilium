import time


class Test:
    def __init__(self, url):
        self.test_url = url

    def __call__(self, runtime, result=None, *args):
        """"""
        runtime.communication.simulate(self.test_url)
        while True:
            time.sleep(0.1)
            stack = runtime.storage.get()
            for sut in runtime.application.sut.values():
                if sut.name in stack and self.test_url in stack[sut.name]:
                    continue
                else:
                    break
            else:
                break
        for validator in runtime.validators:
            validator.validate(self.test_url, runtime.storage,
                               runtime.application.sut.values(),
                               runtime.application.stub)
