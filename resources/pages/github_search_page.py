# left sidebar
repositories_menu = "//*[contains(@class,'menu-item') and descendant::text()='Repositories']"
repositories_count = "//*[@data-search-type='Repositories']"


# search results
repository_title = "//div[@class='f4 text-normal']"
def repository_title_with_text(text): return f"{repository_title}/*[contains(.,'{text}')]"
