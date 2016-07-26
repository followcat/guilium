import selenium.webdriver
import selenium.webdriver.chrome.options
import selenium.webdriver.firefox.options

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
        if 'browser name' in self.config:
            browser = self.config['browser name']
            if browser in ['IE', 'Internet Explorer', 'ie', 'internet explorer']:
                self.driver = self.start_ie()
            elif browser in ['Chrome', 'chrome', 'Google Chrome', 'google chrome']:
                self.driver = self.start_chrome()
            elif browser in ['Firefox', 'firefox', 'ff', 'FF']:
                self.driver = self.start_firefox()
        elif 'device name' in self.config:
            self.driver = self.start_chrome(emulation=True)
        self.driver.maximize_window()

    def start_ie(self):
        desired_caps = selenium.webdriver.DesiredCapabilities.INTERNETEXPLORER
        desired_caps['ignoreZoomSetting'] = True
        desired_caps['nativeEvents'] = False
        driver = selenium.webdriver.Remote(command_executor=self.command_executor, desired_capabilities=desired_caps)
        return driver

    def start_firefox(self):
        desired_caps = selenium.webdriver.DesiredCapabilities.FIREFOX
        profile = None
        if 'profile' in self.config:
            profile = selenium.webdriver.FirefoxProfile(self.config['profile'])
        if self.command_executor is None:
            driver = selenium.webdriver.Firefox(capabilities=desired_caps, firefox_profile=profile)
        else:
            driver = selenium.webdriver.Remote(command_executor=self.command_executor, browser_profile=profile, desired_capabilities=desired_caps)
        return driver

    def start_chrome(self, emulation=False):
        options = selenium.webdriver.chrome.options.Options()
        if emulation:
            mobile_emulation = {"deviceName": self.config['device name']} 
            options.add_experimental_option("mobileEmulation", mobile_emulation)
        if 'profile' in self.config:
                user_data_dir = self.config['profile']
                options.add_argument('--user-data-dir=%s'%user_data_dir)
        if self.command_executor is None:
            driver = selenium.webdriver.Chrome(chrome_options=options)
        else:
            driver = selenium.webdriver.Remote(command_executor=self.command_executor, desired_capabilities=options.to_capabilities())
        return driver

    def stop(self):
        self.driver.quit()

