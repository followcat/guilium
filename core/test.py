class Test:
    def __init__(self, url):
        self.test_url = url

    def __call__(self, runtime, result=None, *args):
        """"""
        runtime.application.stub.process(self.test_url)
