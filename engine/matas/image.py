import engine.matas.base
import engine.processor.image


class ImageMata(engine.matas.base.BaseMata):

    def process(self, url, driver):
        driver.switch_to.context('CHROMIUM')
        driver.get(url)
        image = engine.processor.image.webviewfullscreen(driver)
        return image
