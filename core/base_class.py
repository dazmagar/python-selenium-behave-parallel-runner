from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import *

from core.decorators import log_exception
from utilities.config import Config

import platform
import logging
import time


class BaseClass(object):
    """
    Base class representation.
    Contains all actions related to UI interaction.
    All pages may be inherited from this class.
    """

    def __init__(self, browser):
        """
        :param browser: selenium.webdriver.*
        """
        self.browser = browser
        self.logger = logging.getLogger(self.__class__.__name__)
        self.timeout = 10

    @staticmethod
    def sleep(s):
        time.sleep(s)

    @log_exception('Failed to clean cache and cookies')
    def clean_coockies_and_cache(self):
        if Config.BROWSERNAME == 'Chrome':
            self.browser.delete_all_cookies()
            self.browser.get('chrome://settings/clearBrowserData')
            self.sleep(2)
            ActionChains(self.browser).send_keys(Keys.TAB * 3 + Keys.DOWN * 3).perform()
            self.sleep(2)
            ActionChains(self.browser).send_keys(Keys.TAB * 4 + Keys.ENTER).perform()
            self.sleep(5)  # wait some time to finish

    @log_exception('Failed to get web element with xpath: {}')
    def _get_element(self, element, ec=ec.presence_of_element_located, wait=None):
        """
        Function for getting WebElement from given xpath.
        Also performs highlight of that element if Config.HIGHLIGHT is True.
        :param element: str - web element xpath or can be selenium.webdriver.remote.webelement.WebElement
        :param expected_condition: selenium.webdriver.support.expected_conditions.*
        :param wait: int - element wait time, if None takes self.timeout
        :return: element: selenium.webdriver.remote.webelement.WebElement
        """
        if wait is None:
            wait = self.timeout

        if isinstance(element, str):
            self.logger.debug('Waiting {} seconds for web element with condition: {}'.format(wait, ec.__name__))

            wd_wait = WebDriverWait(self.browser, wait)
            element = wd_wait.until(ec((By.XPATH, element)))

        if element:
            self.logger.debug('Got web element!')

            if Config.HIGHLIGHT:
                self._highlight(element)

        return element

    @log_exception('Failed to get web elements with xpath: {}')
    def get_elements(self, xpath, wait=None):
        """
        Get multiple elements by xpath.
        :param xpath: str - web element xpath
        :param wait: int - wait time for object
        :return: tuple of selenium.webdriver.remote.webelement.WebElement
        """
        self.logger.debug('Getting web elements with xpath: {}'.format(xpath))
        self._get_element(xpath, wait=wait)
        elements = self.browser.find_elements_by_xpath(xpath)
        self.logger.debug('Got web elements with xpath: {}'.format(xpath))
        return elements

    def _highlight(self, element):
        """
        Highlight given web element with red border using JS execution.
        WARNING: Contains time.sleep in 1 sec between scrolling to element and highlighting
        :param element: selenium.webdriver.remote.webelement.WebElement
        """
        self.execute_script(element, 'scrollIntoView(true);')
        self.sleep(1)
        self.execute_script(element, 'setAttribute("style", "color: red; border: 5px solid red;");')
        self.sleep(1)
        self.execute_script(element, 'setAttribute("style", "");')

    @log_exception('Failed presence check of web element with xpath: {}')
    def is_present(self, xpath, expected=True, wait=None):
        """
        Presence check of web element on the UI.
        :param xpath: str - web element xpath
        :param wait: int - wait time for object
        :param expected: boolean - expected to find it
        :return: boolean - element presence
        """
        found = False
        expected_condition = ec.presence_of_element_located
        if not expected:
            expected_condition = ec.staleness_of

        self.logger.info('Checking presence of web element with xpath: {}. Expected: {!s}'.format(xpath, expected))
        found = self._get_element(xpath, expected_condition, wait=wait) is not None
        self.logger.info('Presence check of web element with xpath: {}. Result: {!s}'.format(xpath, found))
        return found

    @log_exception('Failed visible check of web element with xpath: {}')
    def is_visible(self, xpath, expected=True, wait=None):
        """
        Visibility check of web element on the UI.
        :param xpath: str - web element xpath
        :param wait: int - wait time for object
        :param expected: boolean - expected to be visible
        :return: boolean - element visibility
        """
        visible = False
        expected_condition = ec.visibility_of_element_located
        if not expected:
            expected_condition = ec.invisibility_of_element_located

        self.logger.info('Checking visibility of web element with xpath: {}. Expected: {!s}'.format(xpath, expected))
        found = self._get_element(xpath, expected_condition, wait=wait).is_displayed()
        self.logger.info('Visible check of web element with xpath: {}. Result: {!s}'.format(xpath, found))
        return found

    @log_exception('Failed to click web element with xpath: {}')
    def click(self, xpath, wait=None, scroll=True):
        """
        Click web element with given xpath
        :param xpath: str - web element xpath
        :param wait: int - wait time for object
        """
        self.logger.info('Clicking web element with xpath: {}'.format(xpath))
        element = self._get_element(xpath, ec.element_to_be_clickable, wait=wait)
        if scroll:
            self.execute_script(element, 'scrollIntoView(true);')
        element.click()
        self.logger.info('Clicked web element with xpath: {}'.format(xpath))

    def execute_script(self, element, script):
        """
        Execute JavaScript on the web element
        :param element: selenium.webdriver.remote.webelement.WebElement
        :param script: str - JS script body
        :return: result of script execution
        """
        if not element:
            self.logger.error('Element is None. Cannot execute JS')
            raise ValueError('Argument element cannot be None')
        return self.browser.execute_script("return arguments[0].{}".format(script), element)

    @log_exception('Failed to mouse over web element with xpath: {}')
    def mouse_over(self, xpath, wait=None):
        """
        Simulate mouse cursor over given web element.
        :param xpath: str - web element xpath
        :param wait: int - wait time for object
        """
        actions = ActionChains(self.browser)
        actions.move_to_element(self._get_element(xpath, wait=wait)).perform()
        self.logger.info('Mouse over web element with xpath: {}'.format(xpath))

    @log_exception('Failed to mouse over web element with xpath: {}')
    def mouse_over_with_offset(self, xpath, xoffset, yoffset, wait=None):
        """
        Simulate mouse cursor over given web element.
        :param xpath: str - web element xpath
        :param wait: int - wait time for object
        """
        actions = ActionChains(self.browser)
        actions.move_to_element_with_offset(self._get_element(xpath, wait=wait), xoffset, yoffset).perform()
        self.logger.info('Mouse over web element with xpath: {}'.format(xpath))

    @log_exception('Failed to move mouse to coordinates: {}, {}')
    def mouse_move_to_coordinates(self, x, y):
        """
        Simulate mouse cursor move.
        :param x: int
        :param y: int
        """
        actions = ActionChains(self.browser)
        actions.move_by_offset(x, y).perform()

    @log_exception('Failed to drag mouse')
    def mouse_drag(self, x1, y1, x2, y2):
        """
        Simulate drag mouse from x1 y1 to x2 y2.
        :param xpath: str - web element xpath
        """
        actions = ActionChains(self.browser)
        actions.move_by_offset(x1, y1)\
            .click_and_hold()\
            .move_by_offset(x2 - x1, y2 - y1)\
            .release()\
            .perform()
        self.logger.info('Mouse drag for: {}, {}'.format(x2 - x1, y2 - y1))

    @log_exception('Failed open URL: {}')
    def open(self, url):
        """
        Open given URL in browser
        :param url: str - URL to open
        """
        self.browser.get(url)
        self.logger.info('Opened URL: {}'.format(url))

    @log_exception('Failed open new tab: {}')
    def open_new_tab(self):
        """
        Open new tab in browser
        """
        win_handles_befor = self.browser.window_handles
        self.browser.execute_script("window.open('');")
        win_handles_after = self.browser.window_handles
        WebDriverWait(self.browser, self.timeout).until(ec.number_of_windows_to_be(len(win_handles_befor) + 1))
        new_window = [x for x in win_handles_after if x not in win_handles_befor][0]
        self.browser.switch_to_window(new_window)

    @log_exception('Failed to switch tab: {}')
    def switch_to_tab_with_num(self, tab_num):
        """
        Switches driver to new tab only. Works by number of tab, counts from 0.
        """
        self.browser.switch_to_window(self.browser.window_handles[tab_num])

    @log_exception('Cannot switch to frame: {}')
    def switch_to_frame(self, xpath, wait=None):
        """
        Switch to frame
        :param xpath: str - frame xpath
        """
        self.browser.switch_to.frame(self._get_element(xpath, wait=wait))

    @log_exception('Cannot switch to default frame')
    def switch_to_default_frame(self):
        """
        Switch to default frame
        """
        self.browser.switch_to.default_content()

    @log_exception('Cannot get text located: {}')
    def get_text(self, xpath, wait=None):
        """
        Get text of the web element
        :param xpath: str - web element xpath
        :param wait: int - wait time for object
        """
        self.logger.info('Trying to get text from field with xpath: {}'.format(xpath))
        result = self._get_element(xpath, ec.visibility_of_element_located, wait=wait).text
        self.logger.info('Got text "{}" from field with xpath: {}'.format(result, xpath))
        return result

    @log_exception('Failed to type text into web element with xpath: {}')
    def type(self, xpath, text, one_by_one=False, wait=None, lazy_wait=2):
        """
        Type text into input field with given xpath
        :param xpath: str - web element xpath
        :param text: str - text to type
        :param wait: int - wait time for object
        :param lazy_wait: int - wait time for lazy download objects
        """
        self.logger.info('Typing "{}" into field with xpath: {}'.format(text, xpath))
        input_field = self._get_element(xpath, ec.visibility_of_element_located, wait=wait)
        if platform.system() == 'Darwin':   # mac os
            input_field.clear()
        else:                               # others
            input_field.send_keys(Keys.CONTROL, 'a', Keys.DELETE)
        self.sleep(lazy_wait / 2)
        if one_by_one:
            for char in text:
                input_field.send_keys(char)
        else:
            input_field.send_keys(text)
        self.sleep(lazy_wait / 2)
        self.logger.info('Typed "{}" into field with xpath: {}'.format(text, xpath))

    @log_exception('Cannot send ENTER to the web element with xpath: {}')
    def send_enter(self, xpath, wait=None, lazy_wait=1):
        """
        Emulate sending ENTER key from keyboard to the given web element.
        :param xpath: str - web element xpath
        :param wait: int - wait time for object
        :param lazy_wait: int - wait time for lazy download objects
        """
        self._get_element(xpath, wait=wait).send_keys(Keys.ENTER)
        self.sleep(lazy_wait)

    def submit_search(self, xpath, text, wait=None, lazy_wait=2):
        """
        Type text into input field with given xpath and send ENTER key
        :param xpath: str - web element xpath
        :param text: str - text to type
        :param wait: int - wait time for object
        :param lazy_wait: int - wait time for lazy download objects
        """
        self.type(xpath, text, wait=wait, lazy_wait=lazy_wait)
        self.send_enter(xpath, wait=wait, lazy_wait=lazy_wait)

    def get_element_size(self, element_locator, wait=None):
        """
        Return size of element in list
        :param element_locator: str - xpath for element
        :param wait: int - wait time for object
        :return: dict contains width and heigth
        """
        element = self._get_element(element_locator, wait=wait)
        return element.size
