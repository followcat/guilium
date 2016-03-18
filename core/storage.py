class Storage(object):
    """"""

    def __init__(self):
        self.stack = {}

    def set(self, name, data):
        if name not in self.stack:
            self.stack[name] = {}
        self.stack[name].update(data)

    def get(self):
        return self.stack