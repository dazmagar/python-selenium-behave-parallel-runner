from selenium.common.exceptions import *

from core.decorators import log_exception
from core.base_class import BaseClass
from utilities.config import Config
from utilities.common import *


class BasePage(BaseClass):
    """
    Base page representation.
    Class for UI actions related to this page
    """

    # def select_user(self, userName):
    #     TRANSFORMATION_MAP = {
    #         "personalUser": [Config.USER, Config.PASSWORD],
    #         "testActor01": [Config.TESTACTOR01EMAIL, Config.TESTACTOR01PASS],
    #         "testActor02": [Config.TESTACTOR02EMAIL, Config.TESTACTOR02PASS],
    #         "testActor03": [Config.TESTACTOR03EMAIL, Config.TESTACTOR03PASS],
    #         "testActor04": [Config.TESTACTOR04EMAIL, Config.TESTACTOR04PASS],
    #         "testActor05": [Config.TESTACTOR05EMAIL, Config.TESTACTOR05PASS]
    #     }
    #     return TRANSFORMATION_MAP.get(userName)

    def checkObjExists(self, xpath):
        """
        Return True if object exists
        """
        try:
            self.browser.find_element_by_xpath(xpath)
            return True
        except (StaleElementReferenceException, NoSuchElementException):
            return False

    # correct usage:
    # waitForObject(<locator>, state='appear')
    # waitForObject(<locator>, state='disappear')
    @log_exception('Failed check web element state with xpath: {}')
    def waitForObject(self, xpath, state=None, wait=120, lazy_wait=1):
        """
        if state=='disappear', wait until existing object disappeared
        if state=='appear', wait until non-existing object appeared
        :param xpath: str - web element xpath
        :param state: str - switcher for method
        :param wait: int - maximum wait time
        :param lazy_wait: int - additional time for lazy elements
        """
        if state is None or (state.lower() != 'appear' and state.lower() != 'disappear'):
            raise InvalidArgumentException("you should specify 'state' param for method waitForObject every time")

        self.logger.info('Checking web element {} with xpath: {}'.format(state, xpath))
        time_out = 0
        while self.checkObjExists(xpath=xpath) if state.lower() == 'disappear' \
                else not self.checkObjExists(xpath=xpath) if state.lower() == 'appear' else False:

            self.sleep(2)
            time_out += 2
            if time_out > wait:
                raise TimeoutException
        self.logger.info('Checked web element {} with xpath: {}'.format(state, xpath))
        self.sleep(lazy_wait)
