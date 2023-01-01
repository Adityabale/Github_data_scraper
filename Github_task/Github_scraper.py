from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup as bs
import time
import requests
import csv
import os


USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36"
REQUEST_HEADER = { 

    'User-Agent':USER_AGENT,
    'Accept-Language':'en-US, en;q=0.5',

} 

CHROME_DRIVER_PATH = Service(os.path.join(os.getcwd(),"chromedriver.exe"))
OP = webdriver.ChromeOptions() 
OP.add_argument('__headless') 
DRIVER = webdriver.Chrome(service=CHROME_DRIVER_PATH)
time.sleep(2)

def get_page_html(url):
    response = requests.get(url=url, headers=REQUEST_HEADER) 
    return response.content

def soup_repository_tags(html):
    soup = bs(html, "html.parser")
    repository_main = soup.find("div", id="user-repositories-list")
    repository_list = repository_main.find_all("a", attrs={"itemprop":"name codeRepository"})
    return repository_list

def list_of_repositories(l):
    repository_text = [i.text.strip().replace('\n','') for i in l]
    return repository_text

def list_of_repository_urls(l):
    repository_href = [i['href'] for i in l]
    repository_url_list = []
    for j in repository_href:
        repository_url_list.append("https://github.com"+j)
    return repository_url_list

def scraped_data(l,n=0):

    repository_name_star = l[n].find('strong')
    repository_name_star_text = l[n].find('a')
    repository_name_star_textname = repository_name_star_text.text.strip().split()
    repository_name_star_no = repository_name_star.text.strip()
    
    repository_name_watch = l[n+1].find('strong')
    repository_name_watch_text = l[n+1].find('a')
    repository_name_watch_textname = repository_name_watch_text.text.strip().split()
    repository_name_watch_no = repository_name_watch.text.strip()
    
    repository_name_forks = l[n+2].find('strong')
    repository_name_forks_text = l[n+2].find('a')
    repository_name_forks_textname = repository_name_forks_text.text.strip().split()
    repository_name_forks_no = repository_name_forks.text.strip()

    return (repository_name_star_textname[1],repository_name_star_no,repository_name_watch_textname[1],repository_name_watch_no,repository_name_forks_textname,repository_name_forks_no)
    
def extract_repository_details(l):
    repository_names = list_of_repositories(l)
    repository_urls = list_of_repository_urls(l)
    data = []
    m = 0
    for k in repository_urls:
        try:
            response_html=requests.get(url=k)
            repository_name_html = bs(response_html.content, "html.parser")
            repository_name_about = repository_name_html.find('div', {'class':'Layout-sidebar'})
            repository_name_sub = repository_name_about.find_all('div', {'class':'mt-2'})
            
            if len(repository_name_sub) == 3:
                t = scraped_data(repository_name_sub,n=0)
        
            elif len(repository_name_sub) > 3:
                n = len(repository_name_sub)-3
                t = scraped_data(repository_name_sub,n)

        except:
            m=m+1
            continue

        try:
            repository_name_lang_head = repository_name_about.find_all('h2', {'class':'h4 mb-3'})
            repository_name_lang_txt = repository_name_lang_head[2].text
        except:
            repository_name_lang_txt = 'Languages'

        try:
            repository_name_lang_main = repository_name_about.find('span', {'class':'color-fg-default text-bold mr-1'})
            repository_name_lang = repository_name_lang_main.text
        except:
            repository_name_lang = "None"

        repository_details={}

        repository_details['Repository name']=repository_names[m]
        repository_details['stars'] = int(t[1])
        repository_details[str(t[2])] = int(t[3])
        repository_details['forks'] = t[5]
        repository_details['Languages'] = repository_name_lang
        data.append(repository_details)
        m = m+1

    return data

def write_csv(data):
    with open("Github_data.csv",'w') as csvfile:
        header_names = data[0].keys()
        writer = csv.DictWriter(csvfile, fieldnames=header_names)
        writer.writeheader()
        for row in data:
            writer.writerow(row)

def write_csv_append(data):
    with open("Github_data.csv",'a') as csvfile:
        header_names = data[0].keys()
        writer = csv.DictWriter(csvfile, fieldnames=header_names)
        for row in data:
            writer.writerow(row)

if __name__=='__main__':

    base_url="https://github.com/"
    while True:
        username=input("Enter the Github username for scraping data:").strip().replace(' ','')
        DRIVER.get(base_url+username)
        if DRIVER.title == 'Page not found · GitHub · GitHub':
            print('You have entered an invalid username')
            continue
        else:
            break

    time.sleep(2)
    DRIVER.find_element(By.XPATH, value=f"//a[@href='/{username}?tab=repositories']").click()
    time.sleep(2)
    repository_url=DRIVER.current_url
    
    html = get_page_html(repository_url)
    list_= soup_repository_tags(html)
    while True:
        if len(list_) < 30:
            l = list_
            details = extract_repository_details(l)
            write_csv(details)
            DRIVER.close()
            break
        else:
            l = list_
            details = extract_repository_details(l)
            write_csv(details)
            DRIVER.find_element(By.XPATH, value="//a[@class='next_page']").click()
            time.sleep(4)
            repository_url = DRIVER.current_url
            html = get_page_html(repository_url)
            l = soup_repository_tags(html)
            while len(l) == 30:
                details = extract_repository_details(l)
                write_csv_append(details)
                DRIVER.find_element(By.XPATH, value="//a[@class='next_page']").click()
                time.sleep(4)
                repository_url=DRIVER.current_url
                html = get_page_html(repository_url)
                l = soup_repository_tags(html)
            else:
                details = extract_repository_details(l)
                write_csv_append(details)
                DRIVER.close()
                break





