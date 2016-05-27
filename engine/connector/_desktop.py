import selenium.webdriver
import selenium.webdriver.chrome.options

import engine.connector.base


class DesktopConnector(engine.connector.base.Connector):

    def __init__(self, config):
        super(DesktopConnector, self).__init__(config)
        self.command_executor = None
        if 'host' in self.config:
            host = self.config['host']
            if 'port' in self.config:
                port = self.config['port']
            else:
                port = '4444'
            self.command_executor = 'http://%s:%s/wd/hub'%(host, port)

    def start(self):
        if 'browser name' in self.config and self.config['browser name'] == 'IE':
            self.driver = self.start_ie()
        elif 'device name' in self.config:
            self.driver = self.start_chrome(emulation=True)
        else:
            self.driver = self.start_chrome()
        self.driver.maximize_window()

    def start_ie(self):
        desired_caps = selenium.webdriver.DesiredCapabilities.INTERNETEXPLORER
        driver = selenium.webdriver.Remote(command_executor=self.command_executor, desired_capabilities=desired_caps)
        return driver

    def start_chrome(self, emulation=False):
        options = selenium.webdriver.chrome.options.Options()
        if emulation:
            mobile_emulation = {"deviceName": self.config['device name']} 
            options.add_experimental_option("mobileEmulation", mobile_emulation)
        if 'user data dir' in self.config:
                user_data_dir = self.config['user data dir']
                options.add_argument('--user-data-dir=%s'%user_data_dir)
        if self.command_executor is None:
            driver = selenium.webdriver.Chrome(chrome_options=options)
        else:
            driver = selenium.webdriver.Remote(command_executor=self.command_executor, desired_capabilities=options.to_capabilities())
        return driver

    def stop(self):
        self.driver.quit()

