from selenium.webdriver.common.by import By
from seleniumwire import webdriver
from selenium.webdriver.chrome.service import Service
import time
import random
from bs4 import BeautifulSoup
import re

import lib.config


class UseSelenium:

    item_value_title = 'Разрешение экрана'

    def __get_headers_proxy(self) -> dict:
        '''
        The config file must have two dicts:
            USER_AGENTS_LIST = [
                'user_agent',
            ]

            PROXY_LIST = [
                'https://user:passw@ip:port',

            ]
        '''

        try:

            persona = {'http_proxy': random.choice(lib.config.PROXY_LIST),
                       'user-agent': random.choice(lib.config.USER_AGENTS_LIST)}
        except ImportError:
            persona = None
        return persona

    def _connect_to_page(self, url):
        persona = self.__get_headers_proxy()

        options = webdriver.ChromeOptions()
        options.add_argument(f"user-agent={persona['user-agent']}")
        options.add_argument("--disable-blink-features=AutomationControlled")
        # options.add_argument("--start-maximized")
        # options.add_argument("--headless")

        options_proxy = {
            'proxy': {
                'https': persona['http_proxy'],
                'no_proxy': 'localhost,127.0.0.1:8080'
            }
        }

        s = Service(
            executable_path="C:/Users/Matvey/PycharmProjects/pyshop/ozon_parser/selenium_parser/lib/chromedriver.exe")

        driver = webdriver.Chrome(options=options, service=s, seleniumwire_options=options_proxy)
        # disable window methods in browser not to be detected by cloudflare
        driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
            'source': '''
                    delete window.cdc_adoQpoasnfa76pfcZLmcfl_Array;
                    delete window.cdc_adoQpoasnfa76pfcZLmcfl_Promise;
                    delete window.cdc_adoQpoasnfa76pfcZLmcfl_Symbol;
                    '''
        })

        driver.get(url)

        return driver

    def parse_item(self, url):
        print(url)
        driver = self._connect_to_page(url)
        soup = BeautifulSoup(driver.page_source, features="lxml")
        print("Parsing product's data...")

        try:

            property_title_span = soup.find('span', text=re.compile(self.item_value_title), recursive=True)

            property_value = property_title_span.parent.next_sibling.text

            return {'status': 'ok', 'value': property_value}
        except:
            return {'status': 'error'}

    def get_items_links(self, url):
        driver = self._connect_to_page(url)

        try:
            time.sleep(10)

            print("waiting 20s for page to fully load...")
            driver.execute_script("window.scrollTo(5,8000);")
            time.sleep(20)

            soup = BeautifulSoup(driver.page_source, features="lxml")
            links = []
            for a_tag in soup.find_all('a', class_='tile-hover-target'):
                links.append(a_tag['href'])

            links = list(set(links))

            link_dicts = []
            for link in links:
                link_state = {'link':  link, 'parsed': False, 'value': None}
                link_dicts.append(link_state)

            return link_dicts

        except Exception as ex:
            print(ex)
        finally:
            driver.close()
            driver.quit()

