class BaseValidator(object):

    def __init__(self):
        self._type = self.__module__.split('.')[-1]

    @property
    def type(self):
        return self._type

    def validate(self):
        """"""
