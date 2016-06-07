import core.test


def urls():

    return ['http://10.0.0.119:5000/',
            'http://10.0.0.119:5000/text',
            'http://10.0.0.119:5000/textlayout',
            'http://10.0.0.119:5000/image',
            'http://10.0.0.119:5000/mismatch',
            'http://www.baidu.com/',
            'http://www.bing.com/',
            'http://www.microsoft.com/zh-cn',
            'http://www.msn.com',
            'https://www.taobao.com',
            'http://www.smzdm.com',
            'http://www.sohu.com',
            'http://wwww.sina.com.cn',
            'http://www.chinarank.org.cn',
            'http://www.jd.com',
            'http://www.so.com',
            'http://www.zhaopin.com',
            'http://www.163.com',
            'http://www.ifeng.com',
            'http://www.51job.com',
            'http://www.cntv.cn',
            'http://www.chinanews.com',
            'http://www.youku.com',
            'http://www.ganji.com',
            ]

def TestGenerator():
    for test in core.test.test_generator(urls()):
        yield test
