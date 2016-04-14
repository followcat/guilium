class BaseMata(object):
    """"""
    @property
    def type(self):
        self._type = self.__module__.split('.')[-1]
        return self._type

    def process(self):
        """"""
