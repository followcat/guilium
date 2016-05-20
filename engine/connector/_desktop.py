import selenium.webdriver
import selenium.webdriver.chrome.options

import engine.connector.base


class DesktopConnector(engine.connector.base.Connector):

    def __init__(self, config):
        super(DesktopConnector, self).__init__(config)
        device_name = self.config['device name']
        self.command_executor = None
        if 'host' in self.config:
            host = self.config['host']
            if 'port' in self.config:
                port = self.config['port']
            else:
                port = '4444'
            self.command_executor = 'http://%s:%s/wd/hub'%(host, port)
        mobile_emulation = {"deviceName": device_name} 
        self.options = selenium.webdriver.chrome.options.Options()
        self.options.add_experimental_option("mobileEmulation", mobile_emulation)

    def start(self):
        if self.command_executor is None:
            self.driver = \
                selenium.webdriver.Chrome(chrome_options=self.options)
        else:
            self.driver = selenium.webdriver.Remote(command_executor=self.command_executor, desired_capabilities=self.options.to_capabilities())
        self.driver.maximize_window()

    def stop(self):
        self.driver.quit()

