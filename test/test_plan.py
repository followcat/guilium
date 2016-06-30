import json

import core.test


def TestGenerator(test_list):
    urls = json.loads(test_list)
    for test in core.test.test_generator(urls):
        yield test
