import time
import socket 
import threading
import subprocess

import appium.webdriver

import engine.connector.base


get_assign_port_lock = threading.Lock()

def pickfreeport():
    with get_assign_port_lock:
        _socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        _socket.bind(('127.0.0.1', 0))
        addr, port = _socket.getsockname()
        _socket.close()
    return port

def start_appium_in_subprocess(desired_caps=None, port=None):
        """
            >>> import time
            >>> import engine.connector._mobile as mb
            >>> desired_caps = {'avd': 'avd5.1_new'}
            >>> p, port = mb.start_appium_in_subprocess(desired_caps)
            >>> time.sleep(5)
            >>> p.terminate()
            >>> s = p.stdout.readlines()
            >>> "Appium REST http interface listener started" in s[-1]
            True
        """
        if port is None:
            port = pickfreeport()
        bootstrap_port = pickfreeport()
        chromedriver_port = pickfreeport()
        start_caps = ''
        if desired_caps is not None:
            if 'udid' in desired_caps:
                start_caps = '--default-capabilities={"udid":"%s"}' \
                                % desired_caps['udid']
            elif 'avd' in desired_caps:
                start_caps = '--default-capabilities={"avd":"%s"}' \
                                % desired_caps['avd']
        command = ['appium',
                   '--command-timeout=300',
                   '-p', str(port),
                   '-bp', str(bootstrap_port),
                   '--chromedriver-port', str(chromedriver_port)]
        if len(start_caps) > 0:
            command.append(start_caps)
        proc = subprocess.Popen(command,
                    stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        return proc, port


class MobileConnector(engine.connector.base.Connector):

    def __init__(self, config):
        super(MobileConnector, self).__init__(config)
        self.desired_caps = {
            'browserName': 'Browser',
            'platformName': 'Android',
            'platformVersion': '4.4',
            'deviceName': 'Android Emulator',
            'udid': self.config['udid']
        }

    def start(self):
        self.server, server_port = start_appium_in_subprocess(
            self.desired_caps)
        while(True):
            outstr = self.server.stdout.readline()
            if "Appium REST http interface listener started on" in outstr:
                break

        command_executor = 'http://localhost:%s/wd/hub'% server_port
        try:
            self.driver = \
                appium.webdriver.Remote(command_executor, self.desired_caps)
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
        self.server.terminate()

