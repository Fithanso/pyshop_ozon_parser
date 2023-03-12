import json

from selenium_pages import UseSelenium


class Parser:

    def __init__(self):
        self.max_items = 100
        self.links_found = 0
        self.items = []
        self.url_template = "https://www.ozon.ru/category/smartfony-15502/?page="
        self.site_index_url = "https://www.ozon.ru"

    def get_items_links(self):
        page_counter = 1
        open('items_links_plain_text.txt', 'w').close()
        open('items_statuses.json', 'w').close()

        while self.links_found < self.max_items:
            url = self.url_template + str(page_counter)
            item_links = UseSelenium().get_items_links(url)
            allocated_quantity = self.__allocate_items_quantity(item_links)
            items_to_parse = item_links[:allocated_quantity]

            print(f'On page №{page_counter} I found {len(item_links)} links.')
            print(f'{allocated_quantity} of them were written to output file.')
            print(url)

            with open('items_links_plain_text.txt', 'a') as f:
                for item in items_to_parse:
                    f.write(f"{item['link']}\n")

            self.items += items_to_parse
            self.links_found += allocated_quantity

            page_counter += 1

        with open('items_statuses.json', 'w', encoding='utf-8') as f:
            json.dump(self.items, f, ensure_ascii=False, indent=4)

    def parse_items(self, items):

        all_items_parsed = True
        for item in items:
            if not item['parsed']:
                item_url = self.site_index_url+item['link']
                result = UseSelenium().parse_item(item_url)
                print('Result:', result)
                if result['status'] == 'ok':
                    item['parsed'] = True
                    item['value'] = result['value']
                elif result['status'] == 'error':
                    all_items_parsed = False

        with open('items_statuses.json', 'w', encoding='utf-8') as f:
            json.dump(items, f, ensure_ascii=False, indent=4)

        return all_items_parsed

    def parse_until_completion(self):
        with open('items_statuses.json', 'r', encoding='utf-8') as f:
            items = json.load(f)
        all_items_parsed = False

        while not all_items_parsed:
            all_items_parsed = self.parse_items(items)

    def __allocate_items_quantity(self, item_links):
        allocated_quantity = len(item_links)

        if self.links_found + len(item_links) > self.max_items:
            allocated_quantity = len(item_links) - (self.links_found + len(item_links) - self.max_items)

        return allocated_quantity


if __name__ == '__main__':
    p = Parser()
    # p.get_items_links()
    p.parse_until_completion()
