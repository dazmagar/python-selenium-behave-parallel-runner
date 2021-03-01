import selenium.webdriver as webdriver
import configparser
import os


class Config(object):
    """
    Config class for storing values from config.ini and browser types.
    """
    browser_types = \
        dict(Chrome=webdriver.Chrome, Firefox=webdriver.Firefox, Edge=webdriver.Edge, Remote=webdriver.Remote)

    # start # browser configs only for local runs
    download_path = os.getcwd() + "/resources/downloads/"  # IMPORTANT - ENDING SLASH V IMPORTANT

    CHROME_OPTIONS = webdriver.ChromeOptions()
    prefs = {"profile.default_content_settings.popups": 0,
             "download.default_directory": download_path,
             "directory_upgrade": True}
    CHROME_OPTIONS.add_experimental_option('prefs', prefs)
    CHROME_OPTIONS.add_argument('--ignore-certificate-errors')
    CHROME_OPTIONS.add_argument('--ignore-ssl-errors')

    CAPABILITIES = webdriver.DesiredCapabilities.CHROME
    CAPABILITIES['goog:loggingPrefs'] = {'performance': 'ALL'}

    # end # browser configs only for local runs

    config = configparser.RawConfigParser()  # .ConfigParser()
    config.read('config.ini')

    HIGHLIGHT = config.getboolean('SELENIUM', 'Highlight')
    REUSE = config.getboolean('SELENIUM', 'Reuse')

    BROWSERTYPE = config.get('BROWSER', 'BrowserType')
    PLATFORM = config.get('BROWSER', 'Platform')
    BROWSERNAME = config.get('BROWSER', 'BrowserName')
    VERSION = config.get('BROWSER', 'Version')

    # application
    APP_URL = config.get('APPLICATION', 'APP_URL')
    # ENV = config.get('APPLICATION', 'ENV')
    # APP_URL = config.get('APPLICATION', 'APP_URL').replace("ENV", ENV)
    # POPUP_URL = config.get('APPLICATION', 'POPUP_URL')
    PROJECT_DB = config.get('APPLICATION', 'PROJECT_DB')

    # users
    # USER = config.get('USERS', 'userIdTemp')
    # PASSWORD = config.get('USERS', 'passwordTemp')
    # TESTACTOR01EMAIL = config.get('USERS', 'testActor01Email')
    # TESTACTOR02EMAIL = config.get('USERS', 'testActor02Email')
    # TESTACTOR03EMAIL = config.get('USERS', 'testActor03Email')
    # TESTACTOR04EMAIL = config.get('USERS', 'testActor04Email')
    # TESTACTOR05EMAIL = config.get('USERS', 'testActor05Email')
    # TESTACTOR01PASS = config.get('USERS', 'testActor01Pass')
    # TESTACTOR02PASS = config.get('USERS', 'testActor02Pass')
    # TESTACTOR03PASS = config.get('USERS', 'testActor03Pass')
    # TESTACTOR04PASS = config.get('USERS', 'testActor04Pass')
    # TESTACTOR05PASS = config.get('USERS', 'testActor05Pass')

    # logging
    LOG_DIR = os.path.abspath('logs')
