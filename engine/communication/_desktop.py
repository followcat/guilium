import selenium.webdriver
import selenium.webdriver.chrome.options

import engine.communication.base


class Communication(engine.communication.base.Communication):

    def __init__(self, name):
        super(Communication, self).__init__(name)
        mobile_emulation = { 
            "deviceMetrics": {
                "width": 480,
                "height": 800,
                "pixelRatio": 3.0},
            "userAgent": "Mozilla/5.0 (Linux; Android 5.1.1; "
                         "en-us; Nexus 5 Build/JOP40D) "
                         "AppleWebKit/535.19 (KHTML, like Gecko) "
                         "Chrome/18.0.1025.166 Mobile Safari/535.19"}
        self.options = selenium.webdriver.chrome.options.Options()
        self.options.add_experimental_option("mobileEmulation", mobile_emulation)

    def start(self):
        self.driver = selenium.webdriver.Chrome(chrome_options=self.options)

    def stop(self):
        self.driver.quit()

