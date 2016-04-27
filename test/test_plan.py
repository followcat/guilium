import core.test


def urls():

    return ['http://localhost:5000/',
            'http://localhost:5000/text',
            'http://localhost:5000/textlayout',
            'http://localhost:5000/image',
            'http://www.willendare.com/',
            'http://www.baidu.com/',
            'http://www.bing.com/',
            ]

def TestGenerator():
    for url in urls():
        yield core.test.Test(url), url
