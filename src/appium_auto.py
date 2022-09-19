import time
from appium import webdriver
from appium.webdriver.common.touch_action import TouchAction
from appium.webdriver.common.appiumby import AppiumBy
import logging
from src.image_tool import ImageTool


class AndroidAppium:
    def __init__(self, desired_caps=None):
        if desired_caps:
            self.desired_caps = desired_caps
        else:
            self.desired_caps = {
                'platformName': 'Android',  # Android device
                'newCommandTimeout': 60000,
                'automationName': 'UiAutomator2',
                'autoGrantPermissions': True
            }
        # connect to Appium Server
        self.driver = webdriver.Remote('http://localhost:4723/wd/hub', self.desired_caps)

        # Set up logger
        self.logger = logging.getLogger("Appium_logger")
        self.logger.propagate = False
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            handler.setLevel(logging.INFO)
            formatter = logging.Formatter('%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s')
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
        self.logger.debug('Appium Server starts')

    @property
    def device_width(self):
        return self.driver.get_window_size()['width']

    @property
    def device_height(self):
        return self.driver.get_window_size()['height']

    def disable_dv(self):
        # self.driver.implicitly_wait(5)
        self.driver.find_element_by_xpath('//android.widget.ImageView[@content-desc="More options"]').click()
        self.driver.implicitly_wait(0.5)
        element = self.driver.find_elements_by_id(
            'com.google.android.exoplayer2.demo:id/checkbox')[0]
        try:
            assert element.get_attribute("checked") == False
        except:
            element.click()
            self.logger.info('Disabled Dolby Vision.')
        else:
            self.logger.info('Already disabled Dolby Vision.')
            self.back()

    def enable_dv(self):
        # self.driver.implicitly_wait(5)
        self.driver.find_element_by_xpath('//android.widget.ImageView[@content-desc="More options"]').click()
        self.driver.implicitly_wait(0.5)
        element = self.driver.find_elements_by_id(
            'com.google.android.exoplayer2.demo:id/checkbox')[0]
        try:
            assert element.get_attribute("checked") == False
        except:
            self.logger.info('Already enabled Dolby Vision.')
            self.back()
        else:
            element.click()
            self.logger.info('Enabled Dolby Vision.')

    def back(self):
        self.driver.keyevent(4)
        self.logger.info('Back')

    def swipe(self, direction=1):
        """
        :param direction: 0 for up direction, 1 for down direction
        :return: True for scrolled, False for not (page didn't change)
        """
        self.driver.save_screenshot("../screenshots/before.png")
        match direction:
            case 0:  # goes up
                self.driver.swipe(self.device_width * 0.5, self.device_height * 0.35, self.device_width * 0.5,
                                  self.device_height * 0.65, 100)
                self.logger.info(f'Scrolling up.')
            case 1:  # goes down
                self.driver.swipe(self.device_width * 0.5, self.device_height * 0.65, self.device_width * 0.5,
                                  self.device_height * 0.35, 100)
                self.logger.info(f'Scrolling down.')
        time.sleep(0.5)
        self.driver.save_screenshot("../screenshots/after.png")
        if ImageTool.cmpimg("../screenshots/before.png", "../screenshots/after.png") >= 0.95:
            self.logger.warning('Reach the end! Stop scrolling.')
            return False
        return True

    def click_on(self, name):
        """
        :param name: text name you want to click on
        :return: True for clicked, False for not
        """
        if self.is_element_exist(name):
            self.driver.find_element_by_android_uiautomator(f'text("{name}")').click()
            self.logger.info(f'Click on {name}')
            return True
        else:
            self.logger.debug(f'Click operation not performed')
            return False

    def is_element_exist(self, name):
        """

        :param name: text name you want to check if it exists on the page
        :return: True for exists, False for not
        """
        self.driver.implicitly_wait(0.5)
        if not self.driver.find_elements_by_android_uiautomator(f'text("{name}")'):
            self.logger.debug(f'{name} does not exist.')
            return False
        else:
            self.logger.debug(f'{name} exists.')
            return True

    def set_landscape(self):
        self.driver.orientation = "LANDSCAPE"
        self.logger.info('Setting orientation to LANDSCAPE')

    def launch_exoplayer(self):
        self.driver.activate_app("com.google.android.exoplayer2.demo")
        self.logger.info('Launch Exoplayer.')

    def exit_exoplayer(self):
        for i in range(3):
            self.driver.press_keycode(4)

        self.driver.terminate_app("com.google.android.exoplayer2.demo")
        self.logger.info('Quit Exoplayer.')
        # self.driver.close_app()

    def launch_gallery(self):
        self.driver.activate_app("com.android.fileexplorer")
        self.logger.info('Launch Files App.')

    def exit_gallery(self):
        for i in range(3):
            self.driver.press_keycode(4)

        self.driver.terminate_app("com.android.fileexplorer")
        self.logger.info('Quit Files App.')

    def drag_seekbar(self, num):
        seekbar = self.driver.find_element_by_id("com.google.android.exoplayer2.demo:id/exo_progress")
        width = seekbar.size.get('width')
        x = seekbar.location.get('x')
        y = seekbar.location.get('y')
        self.driver.save_screenshot("../screenshots/before.png")
        self.driver.swipe(x, y, int(width * num * 0.01), y, 1000)
        time.sleep(0.5)
        logging.debug("Start dragging.")
        self.driver.save_screenshot("../screenshots/after.png")
        if ImageTool.cmpimg("../screenshots/before.png", "../screenshots/after.png") >= 0.95:
            self.logger.warning('Nothing changed. UI stayed the same.')
            return False
        else:
            self.logger.info('UI changed.')
            return True


class IOSAppium:
    def __init__(self, device_name, udid, device_os_version, desired_caps=None):
        if desired_caps:
            self.desired_caps = desired_caps
        else:
            self.desired_caps = {
                'platformName': 'iOS',
                'platformVersion': f'{device_os_version}',
                'deviceName': f'{device_name}',
                'udid': f'{udid}',
                'xcodeOrgId': 'S685K36NXH',
                'xcodeSigningId': 'iPhone Developer',
                'newCommandTimeout': 60000,
                'automationName': 'XCUITest',
                'autoGrantPermissions': True,
                # 'bundleId': "com.globallogic.dvdecoding"
            }
        # connect to Appium Server
        self.driver = webdriver.Remote('http://localhost:4723/wd/hub', self.desired_caps)
        # Set up logger
        self.logger = logging.getLogger("Appium_logger")
        self.logger.propagate = False
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            handler.setLevel(logging.INFO)
            formatter = logging.Formatter('%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s')
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
        self.logger.info('Appium Server starts')

    @property
    def device_width(self):
        return self.driver.get_window_size()['width']

    @property
    def device_height(self):
        return self.driver.get_window_size()['height']

    def back(self):
        self.driver.keyevent(4)

    def swipe(self, direction=1):
        """
        :param direction: 0 for up direction, 1 for down direction
        :return: True for scrolled, False for not (page didn't change)
        """
        self.driver.save_screenshot("../screenshots/before.png")
        match direction:
            case 0:  # goes up
                self.driver.swipe(self.device_width * 0.5, self.device_height * 0.35, self.device_width * 0.5,
                                  self.device_height * 0.65, 100)
                self.logger.info(f'Scrolling up.')
            case 1:  # goes down
                self.driver.swipe(self.device_width * 0.5, self.device_height * 0.65, self.device_width * 0.5,
                                  self.device_height * 0.35, 100)
                self.logger.info(f'Scrolling down.')
        time.sleep(0.5)
        self.driver.save_screenshot("../screenshots/after.png")
        if ImageTool.cmpimg("../screenshots/before.png", "../screenshots/after.png") >= 0.95:
            self.logger.warning('Reach the end! Stop scrolling.')
            return False
        return True

    def click_on(self, name):
        """
        :param name: text name you want to click on
        :return: True for clicked, False for not
        """
        element = self.is_element_exist(name)
        if element:
            element.click()
            # action = TouchAction(self.driver)
            self.logger.info(f"Click on {name}")
            time.sleep(0.5)
            return True
        else:
            self.logger.debug(f'Click operation not performed')
            return False

    def is_element_exist(self, name):
        """
        :param name: text name you want to check if it exists on the page
        :return: element for exists, False for not
        """
        self.driver.implicitly_wait(0.5)
        res1 = self.driver.find_elements(AppiumBy.IOS_PREDICATE, r'label CONTAINS "%s"' % name)
        res2 = self.driver.find_elements(AppiumBy.XPATH,r'//XCUIElementTypeButton[@name="%s"]' % name)
        if res1:
            self.logger.debug(f'{name} exists.')
            return res1[0]
        elif res2:
            self.logger.debug(f'{name} exists.')
            return res2[0]
        else:
            self.logger.debug(f'{name} does not exist.')
            return False

    def set_landscape(self):
        self.driver.orientation = "LANDSCAPE"
        self.logger.info('Setting orientation to LANDSCAPE')

    def set_portrait(self):
        self.driver.orientation = 'PORTRAIT'
        self.logger.info('Setting orientation to PORTRAIT')

    def launch_ios_sample_player(self):
        self.driver.activate_app("com.globallogic.dvdecoding")
        self.logger.info("Launch ios sample player")

    def exit_ios_sample_player(self):
        self.driver.terminate_app("com.globallogic.dvdecoding")
        self.logger.info("Exit ios sample player")
        # self.driver.close_app()

    def launch_ios_unit_test(self):
        self.driver.activate_app("com.dolby.ios-unit-test")

    def exit_ios_unit_test(self):
        self.driver.terminate_app("com.dolby.ios-unit-test")
        # self.driver.close_app()

    def launch_files_app(self):
        self.driver.activate_app("com.apple.DocumentsApp")
        self.logger.info("Launch File app")

    def exit_files_app(self):
        self.driver.terminate_app("com.apple.DocumentsApp")
        self.logger.info("Exit Files app")

    def play_back(self):
        self.click_on("play")
        self.logger.info("Play")

    def click_screen_center(self):
        action = TouchAction(self.driver)
        x= self.device_width // 2
        y = self.device_height // 2
        action.tap(None, x, y, 1)
        self.logger.debug(f"Tap on ({x}, {y})")
        time.sleep(0.5)

    def disable_dv(self):
        self.driver.find_element_by_ios_predicate(r'label == "settings"').click()
        time.sleep(0.5)
        switch = self.driver.find_element(AppiumBy.IOS_CLASS_CHAIN,r'**/XCUIElementTypeSwitch[`label == "DVA Processing"`]')
        if switch.get_attribute("value"):
            switch.click()
            self.logger.info("Disabled DV.")
        else:
            self.logger.info("Already disabled DV.")
        self.driver.find_element(AppiumBy.IOS_CLASS_CHAIN,r'**/XCUIElementTypeButton[`label == "My Movies"`]').click()

    def enable_dv(self):
        self.driver.find_element_by_ios_predicate(r'label == "settings"').click()
        time.sleep(0.5)
        switch = self.driver.find_element(AppiumBy.IOS_CLASS_CHAIN,r'**/XCUIElementTypeSwitch[`label == "DVA Processing"`]')
        if not switch.get_attribute("value"):
            switch.click()
            self.logger.info("Enabled DV.")
        else:
            self.logger.info("Already enabled DV.")
        self.driver.find_element_by(AppiumBy.IOS_CLASS_CHAIN,r'**/XCUIElementTypeButton[`label == "My Movies"`]').click()

    def __exit__(self):
        self.driver.quit()
        self.logger.info("Appium exit")
