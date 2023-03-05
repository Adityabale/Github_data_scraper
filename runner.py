import os
import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service

from github_scraper import Github_Scraper


def get_driver():
    CHROME_DRIVER_PATH = Service(os.path.join(os.getcwd(), "chromedriver.exe"))
    OP = webdriver.ChromeOptions() 
    OP.add_argument('__headless') 
    driver = webdriver.Chrome(service=CHROME_DRIVER_PATH)
    driver.maximize_window()
    return driver
   
def main():
    driver = get_driver()
    scraper = Github_Scraper()
    while True:
        driver.get(scraper.base_url)
        scraper.username = input("Enter the Github username for scraping data:").strip().replace(' ','')
        driver.get(scraper.base_url+scraper.username)
        if driver.title == 'Page not found · GitHub · GitHub':
            print('You have entered an invalid username')
            continue
        else:
            break
    driver.find_element(By.XPATH, value=f"//a[@href='/{scraper.username}?tab=repositories']").click()
    time.sleep(2)
    html = driver.page_source
    tags= scraper.get_repository_tags(html)
    while True:
        if len(tags) < 30:
            data = scraper.get_repository_data(tags)
            scraper.write_csv(data)
            driver.close()
            break
        else:
            data = scraper.get_repository_data(tags)
            scraper.write_csv(data)
            driver.find_element(By.XPATH, value="//a[@class='next_page']").click()
            time.sleep(2)
            html = driver.page_source
            tags = scraper.get_repository_tags(html)
            while len(tags) == 30:
                data = scraper.get_repository_data(tags)
                scraper.write_csv_append(data)
                driver.find_element(By.XPATH, value="//a[@class='next_page']").click()
                time.sleep(2)
                html = driver.page_source
                tags = scraper.get_repository_tags(html)
            else:
                data = scraper.get_repository_data(tags)
                scraper.write_csv_append(data)
                driver.close()
                break

if __name__=='__main__':
    main()