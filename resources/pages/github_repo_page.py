def repo_name_by_author(author): return f"//*[@itemprop='author' and contains(.,'{author}')]/ancestor::h1//*[@itemprop='name']"
