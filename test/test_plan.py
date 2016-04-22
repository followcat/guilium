import core.test


def urls():

    return ['http://localhost:5000/',
            'http://localhost:5000/mod',
            'http://localhost:5000/content',
            'http://localhost:5000/samplemotor',
            'http://www.baidu.com/']

def TestGenerator():
    for url in urls():
        yield core.test.Test(url), url
