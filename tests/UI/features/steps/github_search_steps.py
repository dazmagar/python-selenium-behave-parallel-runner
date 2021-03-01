from behave import *
from hamcrest import *


@step('I see repositories associated with user and its count greater than "{repo_count}"')
def see_repositories(context, repo_count):
    count = context.github_search_page.get_repositories_count()
    assert_that(count, is_(greater_than(repo_count)))


@step('I navigate into repo with name "{repo_name}"')
def see_repositories(context, repo_name):
    context.github_search_page.open_repo_with_text(repo_name)
