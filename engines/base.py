import time

import _webdriver

class BaseEngine(object):
    """"""
    def __init__(self, name):
        self.name = name
        self.desired_caps = {
            'browserName': 'Browser',
            'platformName': 'Android',
            'platformVersion': '4.4',
            'deviceName': 'Android Emulator',
            'avd': self.name
        }

    def start(self):
        self.p, port = _webdriver.start_appium_in_subprocess(self.desired_caps)

        while(True):
            outstr = self.p.stdout.readline()
            if "Appium REST http interface listener started on" in outstr:
                break

        command_executor = 'http://localhost:%s/wd/hub'% port
        try:
            self.driver = \
                _webdriver.get_webdriver(command_executor, self.desired_caps)
        except Exception as e:
            self.p.terminate()
            raise e
        self.initaction()

    def initaction(self):
        self.driver.switch_to.context('NATIVE_APP')
        self.driver.tap([(240, 68)])
        time.sleep(0.5)
        self.driver.tap([(20, 68)])
        time.sleep(0.5)
        self.driver.tap([(240, 400)])
        time.sleep(0.5)

    def stop(self):
        self.driver.quit()
        self.p.terminate()
