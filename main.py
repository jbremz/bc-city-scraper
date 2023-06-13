# %%
import config
import requests
from bs4 import BeautifulSoup
from lxml import etree
from tqdm import tqdm
import pandas as pd


def get_soup(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    return soup


def get_lxml_root(url):
    soup = get_soup(url)
    lxml_root = etree.HTML(str(soup))
    return lxml_root


def get_collection_items(lxml_root):
    return lxml_root.xpath('//*[starts-with(@id, "collection-item-container_")]')


def get_item_urls(items):
    return {item.xpath('.//a[@class="item-link"]/@href')[0] for item in items}

def get_band_info(url):
    lxml_root = get_lxml_root(url)
    if lxml_root is None:
        return None
    item_info = lxml_root.xpath('//*[@id="band-name-location"]')[0]
    name = item_info[0].text
    location = item_info[1].text
    return name, location


def scrape_bandcamp_collection():
    lxml_root = get_lxml_root(config.PROFILE)

    items = get_collection_items(lxml_root)
    urls = get_item_urls(items)

    rows = []
    for url in tqdm(urls):
        band_info = get_band_info(url)
        if band_info is None:
            continue
        name, location = band_info
        row = {
            'name': name,
            'location': location,
        }
        rows.append(row)

    df = pd.DataFrame(rows)
    return df

# %%

if __name__ == '__main__':
    df = scrape_bandcamp_collection()
    print(df)