import time
import socket
import threading
import subprocess

import appium.webdriver

import engines.image

class BaseEngine(object):
    """"""
    desired_caps = {
        'browserName': 'Browser',
        'platformName': 'Android',
        'platformVersion': '4.4',
        'deviceName': 'Android Emulator'
    }
    def __init__(self, name):
        self.name = name
        self.get_assign_port_lock = threading.Lock()

    def start(self):
        self.port = self.pickfreeport()
        self.chromedriver_port = self.pickfreeport()
        command = ['appium', '--command-timeout=300',
                   '--avd=%s'%self.name, '-p', str(self.port),
                   '--chromedriver-port', str(self.chromedriver_port)]
        self.p = subprocess.Popen(command,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.STDOUT)
        while(True):
            outstr = self.p.stdout.readline()
            if "Appium REST http interface listener started on" in outstr:
                break
        try:
            self.driver = appium.webdriver.Remote('http://localhost:%s/wd/hub'
                             % self.port, self.desired_caps)
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

    def process(self, url):
        self.driver.switch_to.context('CHROMIUM')
        self.driver.get(url)
        image = engines.image.webviewfullscreen(self.driver)
        return image

    def pickfreeport(self):
        with self.get_assign_port_lock:
            _socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            _socket.bind(('127.0.0.1', 0))
            addr, port = _socket.getsockname()
            _socket.close()
        return port

    def stop(self):
        self.driver.quit()
        self.p.terminate()
