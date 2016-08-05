import time
import functools

import re
import json
import urllib

import core.test


def url_encode(url):
    ret_url = urllib.unquote(url)
    if isinstance(ret_url, unicode):
        ret_url = ret_url.encode('utf')
    pattern = re.compile('=([^&]*)')
    args = pattern.findall(ret_url)
    for arg in args:
        ret_url = ret_url.replace(arg, urllib.quote(arg))
    return ret_url

def test_actions(test, driver):
    url, actions = test
    url = url_encode(url)
    for action in actions:
        if action == 'get' or action[0] == 'get':
            driver.get(url)
            time.sleep(3)
        else:
            e = driver.find_element_by_xpath(action[1])
            y = e.location['y']
            driver.execute_script('window.scrollTo(0, %d-200);'%y)
            if action[0] == 'fill':
                e.clear()
                e.send_keys(action[-1])
            elif action[0] == 'click':
                e.click()
                time.sleep(3)


class Test(core.test.Test):

    def __init__(self, url, ignore_fix_element=False):
        self.test_actions = None
        if isinstance(url, tuple):
            self.test_actions = functools.partial(test_actions, url)
            self.test_url = (url[0], self.test_actions, ignore_fix_element)
        else:
            self.test_url = url


def TestGenerator(test_list):
    """
        >>> import test.test_plan
        >>> content = open('/tmp/test.json').read()
        >>> tests = list(g)
        >>> len(tests)
    """
    urls = json.loads(test_list)
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
            yield Test((url, ('get',)), ignore_fix_element=True), url
