import time


class BaseMata(object):
    """"""
    def __init__(self, config):
        self.config = config

    @property
    def type(self):
        self._type = self.__module__.split('.')[-1]
        return self._type

    def process(self):
        """"""

    def scrollfullscreen(self, driver):
        scroll_height = driver.execute_script('return window.screen.height')
        driver.execute_script('window.scrollTo(0, 0);')
        time.sleep(1)

        moved = 0
        count = 0
        while True:
            last_moved = moved
            driver.execute_script('window.scrollTo(0, %d);' % (count*scroll_height))
            time.sleep(0.3)
            moved = max(driver.execute_script('return document.body.scrollTop'), 
                        driver.execute_script('return document.documentElement.scrollTop')) - last_moved
            if last_moved > moved or (last_moved > 0 and moved == 0):
                break
            if count > 0 and moved == 0:
                break
            count += 1
        driver.execute_script('window.scrollTo(0, 0);')
        return True
