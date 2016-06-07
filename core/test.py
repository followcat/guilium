import functools

def test_actions(test, driver):
    url, actions = test
    for action in actions:
        if action == 'get' or action[0] == 'get':
            driver.get(url)
        else:
            e = driver.find_element_by_xpath(action[1])
            if action[0] == 'fill':
                e.clear()
                e.send_keys(action[-1])
            elif action[0] == 'click':
                e.click()

class Test:
    def __init__(self, url):
        self.test_actions = None
        if isinstance(url, tuple):
            self.test_actions = functools.partial(test_actions, url)
            self.test_url = (url[0], self.test_actions)
        else:
            self.test_url = url

    def __call__(self, runtime, result=None, *args):
        """"""
        runtime.execute(self)
