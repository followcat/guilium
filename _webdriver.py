import socket 
import threading
import subprocess

import appium.webdriver


get_assign_port_lock = threading.Lock()

def pickfreeport():
    with get_assign_port_lock:
        _socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        _socket.bind(('127.0.0.1', 0))
        addr, port = _socket.getsockname()
        _socket.close()
    return port

def start_appium_in_subprocess(avdname=None, udid=None, port=None):
        """
            >>> import time
            >>> import _appium
            >>> p, port = _appium.start_appium_in_subprocess(
            ...             avdname='avd5.1_new')
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
        default_caps = ''
        if udid is not None:
            default_caps = '--default-capabilities={"udid":"%s"}'% udid
        elif avdname is not None:
            default_caps = '--default-capabilities={"avd":"%s"}'% avdname
        command = ['appium',
                   '--command-timeout=300',
                   '-p', str(port),
                   '-bp', str(bootstrap_port),
                   '--chromedriver-port', str(chromedriver_port)]
        if len(default_caps) > 0:
            command.append(default_caps)
        proc = subprocess.Popen(command,
                    stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        return proc, port

def get_webdriver(command_executor, desired_capabilities=None):
    return appium.webdriver.Remote(command_executor, desired_capabilities)
