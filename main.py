# %%

import config
import requests
from bs4 import BeautifulSoup
from lxml import etree
# %%

response = requests.get(config.PROFILE)
soup = BeautifulSoup(response.content, "html.parser")

lxml_root = etree.HTML(str(soup))

# Find elements matching the XPath expression
elements = lxml_root.xpath('//*[@id="collection-item-container_2275094176"]/div[2]/div[2]/a')

# %%

