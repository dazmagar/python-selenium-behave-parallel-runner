from pages.BasePage import BasePage
from resources.pages import github_search_page


class GithubSearchPage(BasePage):
    """
    Github search page representation.
    Class for UI actions related to this page
    """

    def __init__(self, browser):
        """
        :type browser: selenium.webdriver.*
        """
        super(GithubSearchPage, self).__init__(browser)

    def get_repositories_count(self):
        self.waitForObject(github_search_page.repositories_menu, state='appear')
        return self.get_text(github_search_page.repositories_count)

    def open_repo_with_text(self, text):
        self.waitForObject(github_search_page.repository_title_with_text(text), state='appear')
        self.click(github_search_page.repository_title_with_text(text))
