### Feb 29, 2016
    Add core and util in checkmate
    Add checkmate to guilium as sub-module
    Add design diagram in ipython notebook

### Mar 7, 2016
    improve design diagram with internal and external communication

### Mar 16, 2016
    Add base modules (application, component, engine, runtime)
    Add nose plugin
    Add test_plan

### Mar 17, 2016
    Add get/set in storage as communcation
    Update appium process configuration, so can be run in parallel  
    Application can start components

### Mar 18, 2016
    Run components in thread to start appium server in parallel
    Add imagediff validators to compare screenshot images
    Store validation image in test.

### Mar 24, 2016
    Instanize Engines in launcher and pass instances to suts and stub
    Stop appium and driver client when test done
    Support appium 1.5.0(appium 1.4.16 discard)

### Mar 25, 2016
    Launcher hosts suts and stub(Application can be removed)
    Launcher will response to execute tests

### Mar 28, 2016
    Start and run engines of stub and sut in thread(Can run in the same time)

### Apr 11, 2016
    Engine include communication and matas.
    Add dom mata and it's validator.

### Apr 12, 2016
    Add desktop communication and it's matas.
    Add config loader.
    Split dom and image mata to destop and webview version.
