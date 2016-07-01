class Test:
    def __init__(self, test):
        self.test = test

    def __call__(self, runtime, result=None, *args):
        """"""
        runtime.execute(self)
