import socket 
import threading
import subprocess

import appium.webdriver
import selenium.webdriver


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
            >>> import _appium
            >>> desired_caps = {'avd': 'avd5.1_new'}
            >>> p, port = _appium.start_appium_in_subprocess(desired_caps)
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

def get_webdriver(command_executor, desired_capabilities=None):
    return appium.webdriver.Remote(command_executor, desired_capabilities)
