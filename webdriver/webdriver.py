# -*- coding: utf-8 -*-
from time import sleep
from selenium.webdriver import Chrome, ChromeOptions
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from helpers import concat_urls
from webelement import WebElement


class Webdriver:
    def __init__(self, config: dict):
        self.__config = config
        self.__validate_configs()


        if self.__config['auto_start']:
            self.start()


    def __validate_configs(self):
        if not isinstance(self.__config, dict):
            raise Exception('The config object to Chromedriver class must to be a dict.')

        if not 'path' in self.__config.keys():
            raise Exception('Property \'dict\' in config object are required as a string containing absolute path to chromedriver executable.')


        default_configs = {
            'auto_start': False,
            'wait_timeout': 5,
            'wait_for_page_loading': False,
            'page_loading_wait_time': 5,
            'default_tab_name': 'main',
            'default_page': None,
            'base_url': None,
            'options': {},
        }

        for config in default_configs:
            if not config in self.__config.keys():
                self.__config[config] = default_configs[config]


    """
        Get chromedriver options if it is passed.
    """
    def __get_driver_options(self):
        if len(self.__config['options'].keys()) == 0:
            return None

        options = ChromeOptions()
        passed_options = self.__config['options']

        if 'headless' in passed_options.keys() and passed_options['headless'] == True:
            options.add_argument('--headless')
            options.add_argument('--disable-gpu')

        if 'sandbox' in passed_options.keys() and passed_options['sandbox'] == False:
            options.add_argument('--no-sandbox')

        if 'fullscreen' in passed_options.keys() and passed_options['fullscreen'] == True:
            options.add_argument('--start-maximized')

        if 'window_size' in passed_options.keys():
            options.add_argument(f"--window_size={passed_options['window_size'][0]},{passed_options['window_size'][1]}")

        return options


    """
        Start webdriver.
    """
    def start(self):
        driver_options = self.__get_driver_options()

        self.tabs = {}
        self.browser = Chrome(executable_path=self.__config['path'], options=driver_options)

        self.tabs[self.__config['default_tab_name']] = 0
        self.__current_tab = self.__config['default_tab_name']


    """
        Kill chromedriver.
    """
    def stop(self):
        self.browser.quit()
        self.browser = None
        self.tabs = {}


    """
        Restart chromedriver.
    """
    def restart(self):
        self.stop()
        self.start()


    """
        Go to a page in web.
    """
    def go(self, url: str):
        if not 'http' in url:
            if self.__config['base_url'] == None:
                raise Exception('You cannot go to a page without provide a complete valid URL to method \'go\' or a base_url in config object to all Webdriver instance.')

            url = concat_urls(self.__config['base_url'], url)

        self.browser.get(url)

        if self.__config['wait_for_page_loading']:
            sleep(self.__config['page_loading_wait_time'])


    """
        Open a new tab and switch to it (by default, if switch is passed as False, will continue in current tab).
    """
    def new_tab(self, name: str, switch: bool = True):
        if name in self.tabs.keys():
            raise Exception(f'Tab name \'{name}\' are already in use.')

        self.run_js("window.open('', '_blank');")
        self.tabs[name] = len(self.tabs.keys())

        if switch:
            self.browser.switch_to.window(self.browser.window_handles[self.tabs[name]])
            self.__current_tab = name

            if self.__config['default_page'] != None:
                self.go(self.__config['default_page'])


    """
        Switch to a tab.
    """
    def switch_to_tab(self, name: str):
        if name not in self.tabs.keys():
            raise Exception(f'Tab \'name\' does not exists on this Webdriver instance.')

        self.browser.switch_to.window(self.browser.window_handles[self.tabs[name]])
        self.__current_tab = name


    """
        Close a tab.
    """
    def close_tab(self, name: str):
        if name == self.__current_tab:
            raise Exception('Cannot close current tab without switch to another first.')

        current_tab = self.__current_tab

        self.switch_to_tab(name)
        self.browser.close()

        self.switch_to_tab(current_tab)

        self.tabs.pop(name)


    """
        Run js in page and return the result.
    """
    def run_js(self, code: str, args = ()):
        return self.browser.execute_script(code, args)


    """oshi
        Convert a selenium element object into a WebElement instance.
    """
    def prototype_element(self, el):
        return WebElement(el, self.browser, By)


    """
        Get a element identifying the method (can be CSS or XPATH).
    """
    def get_element(self, selector):
        if '//' in selector:
            return self.get_element_by_xpath(selector)
        else:
            return self.get_element_by_css(selector)


    """
        Get element by xpath.
    """
    def get_element_by_xpath(self, path):
        try:
            element = self.browser.find_element(By.XPATH, path)
            return self.prototype_element(element)
        except:
            return None


    """
        Get element by CSS.
    """
    def get_element_by_css(self, selector):
        try:
            element = self.browser.find_element(By.CSS_SELECTOR, selector)
            return self.prototype_element(element)
        except e:
            print(e.message)
            return None


    """
        Get multiple elements identifying the method (can be CSS or XPATH)
    """
    def get_elements(self, selector):
        if '//' in selector:
            return self.get_elements_by_xpath(selector)
        else:
            return self.get_elements_by_css(selector)


    """
        Get multiple elements by xpath.
    """
    def get_elements_by_xpath(self, path):
        try:
            elements = self.browser.find_elements(By.XPATH, path)
            prototyped_elements = []

            for el in elements:
                prototyped_elements.append(self.prototype_element(el))
        except:
            return []


    """
        Get multiple elements by CSS.
    """
    def get_elements_by_css(self, selector):
        try:
            elements = self.browser.find_elements(By.CSS_SELECTOR, selector)
            prototyped_elements = []

            for el in elements:
                prototyped_elements.append(self.prototype_element(el))
        except:
            return []


    """
        Force script to wait until a element is located
    """
    def wait_for_element(self, selector):
        wait_time = 0

        while wait_time <= self.__config['wait_timeout']:
            el = self.get_element(selector)

            if el != None:
                break

            sleep(1)
            wait_time += 1

        if wait_time > self.__config['wait_timeout']:
            raise Exception(f'Cannot localize element with path \'{selector}\' when loading the page.')


    """
        Alias to time.sleep
    """
    def wait(self, seconds: int):
        sleep(seconds)


