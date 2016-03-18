import core.component
import core.communication


class Runtime(object):
    """"""
    def __init__(self, config):
        self.config = config
        self.communication = core.communication
        self.setup_environment()

    def setup_environment(self):
        components = {}
        engines = []
        for sut in self.config.sut:
            components[sut] = core.component.Component(sut, engines)
        self.application = core.application.application(components, self.config.stub)
