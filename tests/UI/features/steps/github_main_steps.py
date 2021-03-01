from behave import *
from hamcrest import *

from utilities.config import Config


@step('I open Github URL in browser')
def open_github(context):
    context.github_main_page.open(Config.APP_URL)


@step('I see "{title}" in title')
def see_title(context, title):
    assert_that(context.browser.title, contains_string(title))


@step('I search "{text}" text')
def search_text(context, text):
    context.github_main_page.github_search(text)
