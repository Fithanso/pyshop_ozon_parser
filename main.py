import asyncio
import re
import json
import datetime
from bs4 import BeautifulSoup

from selenium_pages import UseSelenium
# async режим - 5 минут

class ParsedItem:
    value = None
    from_page = None

    def __init__(self, status):
        self.status = status


class Parser:

    def __init__(self):

        self.url_template = "https://www.ozon.ru/category/smartfony-15502/?page="
        self.site_index_url = "https://www.ozon.ru"
        self.item_value_title = 'Разрешение экрана'

    async def run(self):
        print('parsing started at:', datetime.datetime.now())
        tasks = []
        for page_number in range(1, 4):
            tasks.append(asyncio.create_task(self.parse_page(page_number)))

        await asyncio.gather(*tasks)

    async def parse_page(self, page_number):
        url = self.url_template + str(page_number)
        page_driver = UseSelenium().connect_to_page(url)

        print(f'Now parsing page:', url)
        print("Waiting 20s for page to fully load...")
        page_driver.execute_script("window.scrollTo(5,8000);")
        await asyncio.sleep(20)

        soup = BeautifulSoup(page_driver.page_source, features="lxml")
        parsed_items = []

        for a_tag in soup.find_all('a', class_='tile-hover-target')[:5]:
            parsed_item = await self.parse_item(self.site_index_url + a_tag['href'])
            print(vars(parsed_item))

            if parsed_item.status == 'ok':
                parsed_item.from_page = page_number
                parsed_items.append(parsed_item)

        filename = f'page_{page_number}.json'
        print('creating file:', filename)
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(parsed_items, f)

    async def parse_item(self, url):
        print("Parsing item:", url)
        driver = UseSelenium().connect_to_page(url)
        soup = BeautifulSoup(driver.page_source, features="lxml")

        try:

            property_title_span = soup.find('span', text=re.compile(self.item_value_title), recursive=True)
            property_value = property_title_span.parent.next_sibling.text

            p_item = ParsedItem(status='ok')
            p_item.value = property_value
            return p_item
        except:
            return ParsedItem(status='error')


if __name__ == '__main__':
    p = Parser()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(p.run())
