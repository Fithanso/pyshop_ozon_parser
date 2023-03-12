from bs4 import BeautifulSoup
import re

with open("test.html", encoding="utf-8") as f:
    data = f.read()
    soup = BeautifulSoup(data, features="lxml")

    os_title_span = soup.find('span', text=re.compile('Операционная система'))
    print(os_title_span)
    os_name_div = os_title_span.parent.parent.parent
    print(os_name_div)
    os_version_div = os_name_div.next_sibling
    print(os_version_div)
    os_version_text = os_version_div.find('dd').text
    print()