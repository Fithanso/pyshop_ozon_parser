import json
import re
import time
from bs4 import BeautifulSoup

from selenium_pages import UseSelenium


class Parser:

    def __init__(self):
        self.max_items = 100
        self.total_parsed = 0
        self.url_template = "https://www.ozon.ru/category/smartfony-15502/?page="
        self.site_index_url = "https://www.ozon.ru"
        self.item_value_title = 'Разрешение экрана'

    def run(self):
        page_counter = 1

        while self.total_parsed < self.max_items:
            url = self.url_template + str(page_counter)
            print(f'Now parsing page №{page_counter}: ')
            print(url)
            self.total_parsed += self.parse_page(url)

            page_counter += 1

    def parse_page(self, url):
        page_driver = UseSelenium().connect_to_page(url)

        print("waiting 20s for page to fully load...")
        page_driver.execute_script("window.scrollTo(5,8000);")
        time.sleep(20)

        soup = BeautifulSoup(page_driver.page_source, features="lxml")
        items_parsed = 0

        for a_tag in soup.find_all('a', class_='tile-hover-target'):
            status = self.parse_item(self.site_index_url+a_tag['href'])

            if status['status'] == 'ok':
                items_parsed += 1
                with open('output.txt', 'a', encoding='utf-8') as f:
                    f.write(status['value'] + '\n')

            if self.total_parsed + items_parsed >= self.max_items:
                return items_parsed

        return items_parsed

    def parse_item(self, url):
        print(url)
        driver = UseSelenium().connect_to_page(url)
        soup = BeautifulSoup(driver.page_source, features="lxml")
        print("Parsing product's data...")

        try:

            property_title_span = soup.find('span', text=re.compile(self.item_value_title), recursive=True)

            property_value = property_title_span.parent.next_sibling.text

            return {'status': 'ok', 'value': property_value}
        except:
            return {'status': 'error'}


if __name__ == '__main__':
    p = Parser()
    # p.get_items_links()
    # p.parse_until_completion()
    p.run()
