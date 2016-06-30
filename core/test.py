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

def test_generator(urls):
    for url in urls:
        if isinstance(url, list):
            url = tuple(url)
            last_index = 0
            for index, item in enumerate(url[1]):
                if item == 'test':
                    yield_test = (url[0], url[1][last_index: index])
                    last_index = index + 1
                    yield Test(yield_test), yield_test
            if last_index < len(url[1]):
                yield_test = (url[0], url[1][last_index:])
                yield Test(yield_test), yield_test
        else:
            yield Test((url, ('get',))), url

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
