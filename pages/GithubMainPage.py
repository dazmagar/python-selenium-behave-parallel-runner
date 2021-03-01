from pages.BasePage import BasePage
from resources.pages import github_main_page


class GithubMainPage(BasePage):
    """
    Github main page representation.
    Class for UI actions related to this page
    """

    def __init__(self, browser):
        """
        :type browser: selenium.webdriver.*
        """
        super(GithubMainPage, self).__init__(browser)

    def github_search(self, text):
        self.waitForObject(github_main_page.search_field, state='appear')
        self.submit_search(github_main_page.search_field, text)
