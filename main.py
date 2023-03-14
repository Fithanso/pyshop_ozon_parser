import asyncio
import re
import json
import datetime
from bs4 import BeautifulSoup
import pandas as pd
from art import tprint
import os


from connect_selenium import UseSelenium


class Parser:

    def __init__(self):

        self.url_template = 'https://www.ozon.ru/category/smartfony-15502/?page='
        self.site_index_url = 'https://www.ozon.ru'
        self.item_value_title = 'Разрешение экрана'
        self.page_filename_template = 'temp_page_{}.json'

    def run(self):
        tprint('Ozon  parser')
        start_time = datetime.datetime.now()
        print('Parsing started at:', start_time)

        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.create_tasks())

        end_time = datetime.datetime.now()
        print(f'Parsing ended at: {end_time}. And took: {end_time-start_time}')

    async def create_tasks(self):
        tasks = []
        for page_number in range(1, 4):
            tasks.append(asyncio.create_task(self.parse_page(page_number)))

        await asyncio.gather(*tasks)

    async def parse_page(self, page_number):
        url = self.url_template + str(page_number)
        page_driver = UseSelenium().connect_to_page(url)

        print('Now parsing page:', url)
        print('Waiting 20s for page to fully load...')
        page_driver.execute_script('window.scrollTo(5,8000);')
        await asyncio.sleep(20)

        soup = BeautifulSoup(page_driver.page_source, features='lxml')
        parsed_items = []

        for a_tag in soup.find_all('a', class_='tile-hover-target'):
            parsed_item = await self.parse_item(self.site_index_url + a_tag['href'])

            if parsed_item['status'] == 'ok':
                parsed_item['from_page'] = page_number
                parsed_items.append(parsed_item)

        filename = self.page_filename_template.format(page_number)
        print('Creating file:', filename)
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(parsed_items, f)

    async def parse_item(self, url):
        print('Parsing item:', url)

        try:
            driver = UseSelenium().connect_to_page(url)
            soup = BeautifulSoup(driver.page_source, features='lxml')

            property_title_span = soup.find('span', text=re.compile(self.item_value_title), recursive=True)
            property_value = property_title_span.parent.next_sibling.text

            return {'status': 'ok', 'value': property_value}
        except:
            return {'status': 'error'}


class StatisticCollector:
    output_file_name = 'distribution.csv'
    page_filename_template = 'temp_page_{}.json'
    max_values = 100

    def create_distribution(self, files_qty, delete_temp_files=False):

        parsed_data = []
        for i in range(1, files_qty + 1):
            filename = self.page_filename_template.format(i)
            with open(filename, encoding='utf-8') as f:
                parsed_data += json.load(f)

            if delete_temp_files:
                os.remove(filename)

        parsed_values = [d['value'] for d in parsed_data][:self.max_values]
        parsed_values = self.normalize_symbols(parsed_values)

        df = pd.DataFrame({
            'values': parsed_values,
            'q-ty': [0] * len(parsed_values)
        })

        distribution = df.groupby('values').count().sort_values('q-ty', ascending=False)

        distribution.to_csv(self.output_file_name, sep='\t', encoding='utf-8')

        print('Distribution was written to file:', {self.output_file_name})
        print(distribution)

    def normalize_symbols(self, values_list):

        for i in range(len(values_list)):
            values_list[i] = values_list[i].replace('×', 'x')

        return values_list


if __name__ == '__main__':
    Parser().run()
    StatisticCollector().create_distribution(3)
