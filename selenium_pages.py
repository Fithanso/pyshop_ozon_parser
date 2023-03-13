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

    def connect_to_page(self, url):
        persona = self.__get_headers_proxy()

        options = webdriver.ChromeOptions()
        options.add_argument(f"user-agent={persona['user-agent']}")
        options.add_argument("--disable-blink-features=AutomationControlled")
        # options.add_argument("--start-maximized")
        options.add_argument("--headless")

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


