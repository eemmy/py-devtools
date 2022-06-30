# -*- coding: utf-8 -*-


class WebElement:
    def __init__(self, element, browser, by):
        self.__browser = browser
        self.__by = by
        self.selenium_element = element

        self.text = self.selenium_element.text or None
        self.class_list = self.selenium_element.get_attribute('class') or None
        self.id = self.selenium_element.get_attribute('id') or None
        self.href = self.selenium_element.get_attribute('href') or None
        self.src = self.selenium_element.get_attribute('href') or None

        if isinstance(self.class_list, str):
            self.class_list = self.class_list.split(' ')


    """
        Execute JS using the element as root. Element is referenced as this in this case. Arguments must to start in index 1
    """
    def run_js(self, code):
        code = code.replace('this', 'arguments[0]')

        return self.__browser.execute_script(code, self.selenium_element)


    """
        Trigger events in element via JS.
    """
    def trigger_event(self, event: str):
        self.run_js(f"""
            if (!event)
                var event = new Event('{event}');
            else
                event = new Event('{event}');

            this.dispatchEvent(event);
        """)


    """
        Click in element via js to aviod non-visible or similar errors.
    """
    def click(self):
        self.run_js('this.click();')


    """
        Type in current element.
    """
    def type(self, text):
        self.selenium_element.send_keys(text)


    """
        Set a value to current element (in case of inputs) and trigger onchange event
    """
    def value(self, value):
        self.run_js(f"this.value = '{value}';")
        self.trigger_event('change')


    """
        Get or set attribute value in element via js.
    """
    def attr(self, name, value = None):
        if value == None:
            return self.selenium_element.get_attribute(name)
        else:
            self.run_js(f"this.setAttribute('{name}', '{value}')")


    """
        Remove an attribute from element via js.
    """
    def remove_attr(self, name):
        self.run_js(f"this.removeAttribute('{name}')")


    """
        Find element by xpath using current element as root.
    """
    def get_element_by_xpath(self, path):
        try:
            el = self.selenium_element.find_element(self.__by.XPATH, path)
            return WebElement(el, self.__browser, self.__by)
        except:
            return None


    """
        Find element by CSS using current element as root.
    """
    def get_element_by_css(self, selector):
        try:
            el = self.selenium_element.find_element(self.__by.CSS_SELECTOR, selector)
            return WebElement(el, self.__browser, self.__by)
        except e:
            return None


    """
        Find multiple elements by xpath using current element as root.
    """
    def get_elements_by_xpath(self, path):
        try:
            elements = self.selenium_element.find_elements(self.__by.XPATH, path)
            prototyped_elements = []

            for el in elements:
                prototyped_elements.append(WebElement(el, self.__browser, self.__by))

            return prototyped_elements
        except:
            return []


    """
        Find multiple elements by CSS using current element as root.
    """
    def get_elements_by_css(self, selector):
        try:
            elements = self.selenium_element.find_elements(self.__by.CSS_SELECTOR, selector)
            prototyped_elements = []

            for el in elements:
                prototyped_elements.append(WebElement(el, self.__browser, self.__by))

            return prototyped_elements
        except:
            return []


    """
        Get multiple elements identifying the method (can be CSS or XPATH)
    """
    def get_elements(self, selector):
        if '/' in selector:
            return self.get_elements_by_xpath(selector)
        else:
            return self.get_elements_by_css(selector)


    """
        Get a element identifying the method (can be CSS or XPATH).
    """
    def get_element(self, selector):
        if '/' in selector:
            return self.get_element_by_xpath(selector)
        else:
            return self.get_element_by_css(selector)

