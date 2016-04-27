import core.test


def urls():

    return ['http://localhost:5000/',
            'http://localhost:5000/mod',
            'http://localhost:5000/content',
            'http://localhost:5000/samplemotor',
            'http://www.willendare.com/',
            'http://www.baidu.com/',
            'http://www.bing.com/',
            ]

def TestGenerator():
    for url in urls():
        yield core.test.Test(url), url
