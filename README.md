# guilium
Guilium is the automatic UI testing tools base on checkmate automata.

##  Install

###  Install guilium dependency

install python(2.7.9) and pip(8.0.3):
```
    pip install -r requires.txt
```

install checkmate core:
```
    git clone https://github.com/followcat/checkmate.git
    git checkout dev
    python setup.py install
```

install nodejs(v4.3.1) and npm(2.14.12)
```
    npm install -g appium
```

###  Install checkmate
Install checkmate dependency here:
    https://github.com/followcat/checkmate/blob/master/knowledge/training/setup_environment.rst

### Add device
Android emulator:
    Install Android SDK Manager, download Android SDK tools and any version of android and it‘s Image.
    Create a new emulator.

## Demo
- start your emulator
- run appium server
```
    export ANDROID_HOME=/your/androidsdk/path
    appium
```

- open an ipython then run this script
```
    from appium import webdriver
    desired_caps = {
                'app': 'Browser',
                'platformName': 'Android',
                'platformVersion': PLATFORM_VERSION,
                'deviceName': 'Android Emulator'
            }
    driver = webdriver.Remote('http://localhost:4723/wd/hub', desired_caps)
    driver.quit()
```

## Desgin
Using ipython notebook to get doc information, like
```
    ipython notebook doc/design.ipynb
```

## License
All the codes in this project are under the GPL3+ License.
