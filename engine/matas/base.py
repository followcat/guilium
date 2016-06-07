import time


class BaseMata(object):
    """"""
    def __init__(self, config):
        self.config = config

    @property
    def type(self):
        self._type = self.__module__.split('.')[-1]
        return self._type

    def process(self):
        """"""
