from behave import *
from hamcrest import *


@step('I see that repo "{repo_name}" belongs to "{author}" author')
def see_repositories(context, repo_name, author):
    repo_from_author = context.github_repo_page.check_repo_belongs_to_athor(author)
    assert_that(repo_name, is_(equal_to_ignoring_case(repo_from_author)))
