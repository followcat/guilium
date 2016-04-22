import core.test


def urls():

    return ['http://10.0.0.105:5000/',
            'http://10.0.0.105:5000/mod',
            'http://10.0.0.105:5000/content',
            'http://10.0.0.105:5000/samplemotor',
            'http://www.baidu.com/']

def TestGenerator():
    for url in urls():
        yield core.test.Test(url), url
