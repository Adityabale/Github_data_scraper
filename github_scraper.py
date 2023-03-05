import re
import csv
import requests
from pathlib import Path
from typing import Optional

from bs4 import BeautifulSoup as bs
from selenium.webdriver.remote.webdriver import WebDriver


class Github_Scraper:
    """Scraper class used to get the list of repositories for a defined username
    and also the details associated with each repository like number of stars,
    watching, forks and Languages along with repository name.
    """
    base_url="https://github.com/"

    def __init__(self):
        """Initilize the scraper class"""
        self.driver: Optional[WebDriver] = None
        self.username: str = None

    def get_repository_tags(self, source):
        """Get all the repository tags within beautified html.
        params: source
        Create soup from source html --> get the main div of repositories list --> get all
        repository tags from main div.
        returns: repository_tags
        """
        soup = bs(source, "html5lib")
        repository_div = soup.find("div", id="user-repositories-list")
        repository_tags = repository_div.find_all("a", attrs={"itemprop":"name codeRepository"})
        return repository_tags

    def _get_repository_names(self, tags) -> list[str]:
        """Get repository names from repository tags.
        params: tags
        Iterate over each tag element --> get the text --> replace unnecessary text with
        blank.
        returns: repository_names
        """
        repository_names = [tag.text.strip().replace('\n','') for tag in tags]
        return repository_names

    def _get_repository_urls(self, tags) -> list[str]:
        """Get repository urls from repository tags.
        params: tags
        Iterate over each tag element --> get the href --> attach base url to each relative
        url --> add to list
        returns: repository_urls
        """
        relative_urls = [tag['href'] for tag in tags]
        repository_urls = list()
        for route in relative_urls:
            repository_urls.append(self.base_url+route)
        return repository_urls

    def _get_details(self, sidebar_div) -> list[(str,str)]:
        """Get all the required details from each repo.
         params: sidebar_div
         Get required divs from sidebar div --> iterate over each div --> get head text 
         and value --> add to list --> get language div --> extract head text and value
         add to list.
         returns: repo_details
         """
        repo_details = []
        repo_info_divs = sidebar_div.find_all('div', {'class':'mt-2'})[-3:]
        for info_div in repo_info_divs:
            pattern = re.compile(r"\b[A-Za-z]+\b")
            info_head = pattern.search(info_div.find('a').text.strip()).group()
            if info_head[-1] != 's':
                info_head = ''.join([info_head, 's'])
            if info_head == 'stars':
                value = info_div.find('strong').text.strip()
                repo_details.append((info_head, value))
            elif info_head == 'watchings':
                value = info_div.find('strong').text.strip()
                repo_details.append((info_head, value))
            elif info_head == 'forks':
                value = info_div.find('strong').text.strip()
                repo_details.append((info_head, value))
        repo_lang_head = pattern.search(sidebar_div.find_all("h2", {'class':'h4 mb-3'})[-1].text.strip()).group()
        if repo_lang_head != 'Languages':
            repo_lang_head = 'Languages'
        repo_lang = [pattern.search(lang.text).group() for lang in sidebar_div.find_all('span', {'class':'color-fg-default text-bold mr-1'})]
        if not repo_lang:
            repo_lang = "None"
        repo_details.append((repo_lang_head, repo_lang))
        return repo_details
        
    def get_repository_data(self, tags):
        """Get all repository data from each repository url.
        params: tags
        Get list of repository names and urls from tags --> iterate over each urls --> create
        beautiful soup object with html --> extract sidebar div and get all details --> add 
        details to dict --> also add repository name to dict --> append the dict to list.
        returns: data
        """
        data = list()
        repository_names = self._get_repository_names(tags)
        repository_urls = self._get_repository_urls(tags)
        for name, url in zip(repository_names, repository_urls):
            try:
                repo_html = requests.get(url=url)
                repo_soup = bs(repo_html.content, "html5lib")
                repo_sidebar_div = repo_soup.find('div', {'class':'Layout-sidebar'})
                repo_details = self._get_details(repo_sidebar_div)
                details_dict = {head:value for head, value in repo_details}
                details_dict["repository name"] = name
                data.append(details_dict)
            except Exception:
                pass
        return data

    def write_csv(self, data):
        """Create a csv file in filepath with name as usename and write the same in write
        mode using dictwriter class from csv module.
        """
        self.filepath = Path('scraped-data') / f'{self.username}_details.csv'
        with open(file=self.filepath, mode='w') as csvfile:
            header_names = ["repository name", "stars", "watchings", "forks", "Languages"]
            writer = csv.DictWriter(csvfile, fieldnames=header_names)
            writer.writeheader()
            for row in data:
                writer.writerow(row)

    def write_csv_append(self, data):
        """Write a csv file in append mode in a already existing csv file using dictwriter class 
        from csv module."""
        with open(file=self.filepath, mode='a') as csvfile:
            header_names = ["repository name", "stars", "watchings", "forks", "Languages"]
            writer = csv.DictWriter(csvfile, fieldnames=header_names)
            for row in data:
                writer.writerow(row)
                