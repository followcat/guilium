import selenium.webdriver
import selenium.webdriver.chrome.options

import engine.connector.base


class DesktopConnector(engine.connector.base.Connector):

    def __init__(self, config):
        super(DesktopConnector, self).__init__(config)
        device_name = self.config['device name']
        mobile_emulation = {"deviceName": device_name} 
        self.options = selenium.webdriver.chrome.options.Options()
        self.options.add_experimental_option("mobileEmulation", mobile_emulation)

    def start(self):
        self.driver = selenium.webdriver.Chrome(chrome_options=self.options)
        self.driver.maximize_window()

    def stop(self):
        self.driver.quit()

