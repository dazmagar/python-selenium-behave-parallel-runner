from pages.BasePage import BasePage
from resources.pages import github_repo_page


class GithubRepoPage(BasePage):
    """
    Github repo page representation.
    Class for UI actions related to this page
    """

    def __init__(self, browser):
        """
        :type browser: selenium.webdriver.*
        """
        super(GithubRepoPage, self).__init__(browser)

    def check_repo_belongs_to_athor(self, author):
        self.waitForObject(github_repo_page.repo_name_by_author(author), state='appear')
        return self.get_text(github_repo_page.repo_name_by_author(author))
