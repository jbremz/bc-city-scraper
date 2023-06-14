import argparse
import datetime
import html
import json
import logging
import re
from concurrent.futures import ThreadPoolExecutor

import pandas as pd
import requests
from lxml import html as lxml_html
from tqdm import tqdm


def parse_arguments():
    """
    Parse the command-line arguments.

    Returns:
        argparse.Namespace: Parsed command-line arguments.
    """
    parser = argparse.ArgumentParser(description="Process Bandcamp collection")

    parser.add_argument(
        "--username",
        type=str,
        default="jbremz",
        help="Bandcamp profile URL (overrides jbremz)",
    )

    return parser.parse_args()


def get_initial_collection(username):
    """
    Retrieve the initial collection from the specified profile.

    Returns:
        fan_id (int): the fan's unique identifier
        collection (dict): The collection data.
    """
    logging.info(f"Retrieving initial collection from {username}...")
    profile_url = f"https://bandcamp.com/{username}"
    response = requests.get(profile_url)
    response.raise_for_status()
    data = response.text

    pattern = r'<div id="pagedata" data-blob="(.*?)">'
    matches = re.findall(pattern, data)
    decoded_string = html.unescape(matches[0])
    data = json.loads(decoded_string)
    collection = data["item_cache"]["collection"]
    fan_id = data["fan_data"]["fan_id"]

    return fan_id, collection


def process_collection(collection):
    """
    Process the collection data and convert it to a DataFrame.

    Args:
        collection (dict): The collection data.

    Returns:
        pandas.DataFrame: The processed DataFrame.
    """
    logging.info("Processing collection...")
    rows = []
    for _, item in collection.items():
        row = {}
        row["item_id"] = item["item_id"]
        row["purchased"] = item["purchased"]
        row["item_type"] = item["item_type"]

        timestamp = datetime.datetime.strptime(row["purchased"], "%d %b %Y %H:%M:%S %Z")
        row["unix_time"] = int(timestamp.timestamp())

        rows.append(row)

    df = pd.DataFrame(rows)
    return df


def get_payload(df, fan_id):
    """
    Get the payload by retrieving the newest item in the DataFrame.

    Args:
        df (pandas.DataFrame): The DataFrame.
        fan_id (int): the fan's unique identifier

    Returns:
        dict: The payload for retrieving the newest item.
    """
    logging.info("Getting payload for the newest item...")
    ni = df.loc[df["unix_time"].argmax()]  # newest item
    older_than_token = f"{ni['unix_time']}:{ni['item_id']}:t::"  # TODO include item_type here so it isn't just static
    payload = {"fan_id": fan_id, "older_than_token": older_than_token, "count": 10000}
    return payload


def get_collection(payload):
    """
    Retrieve the collection data using the given payload.

    Args:
        payload (dict): The payload for retrieving the collection.

    Returns:
        dict: The retrieved collection data.
    """
    logging.info("Retrieving collection data...")
    url = "https://bandcamp.com/api/fancollection/1/collection_items"

    try:
        headers = {
            "Content-Type": "application/json",
        }
        response = requests.post(url, data=json.dumps(payload), headers=headers)
        response.raise_for_status()

        data = response.json()
        return data

    except requests.exceptions.RequestException as e:
        logging.error("Error occurred:", exc_info=True)
        return None


def extract_location(url):
    """
    Extract the location from the given band URL.

    Args:
        url (str): The band URL.

    Returns:
        str: The extracted location.
    """
    logging.debug("Extracting location for URL: %s", url)
    try:
        response = requests.get(url)
        response.raise_for_status()

        tree = lxml_html.fromstring(response.content)

        # Use XPath to extract the band name
        location = tree.xpath('//*[@id="band-name-location"]/span[2]/text()')

        return location[0] if location else None

    except requests.exceptions.RequestException as e:
        logging.error("Error occurred:", exc_info=True)
        return None


def process_band_url(url):
    """
    Process the band URL and extract the location.

    Args:
        url (str): The band URL.

    Returns:
        dict: The processed band URL and location.
    """
    logging.debug("Processing band URL: %s", url)
    row = {}
    row["url"] = url
    row["location"] = extract_location(url)
    return row


def split_location(df):
    """
    Split the location column into city and country.

    Args:
        df (pandas.DataFrame): The DataFrame.

    Returns:
        pandas.DataFrame: The DataFrame with split location.
    """
    logging.info("Splitting location 📍")
    df["city"] = df["location"].apply(lambda x: x.split(", ")[0] if x else None)
    df["country"] = df["location"].apply(lambda x: x.split(", ")[1] if x and len(x.split(", ")) > 1 else None)
    df.drop(columns="location", inplace=True)
    return df


def main(username):
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
    logging.info("Location extraction started 🗺️")

    fan_id, collection = get_initial_collection(username)
    df = process_collection(collection)
    payload = get_payload(df, fan_id)
    collection = get_collection(payload)
    band_urls = [item["band_url"] for item in collection["items"]]
    band_urls = list(set(band_urls))

    logging.info("Extracting locations from collection items 🔍")
    rows = []
    with ThreadPoolExecutor(max_workers=3) as executor:  # throttle so as not to kill poor BC
        results = list(tqdm(executor.map(process_band_url, band_urls), total=len(band_urls)))
        rows.extend(results)

    df = pd.DataFrame(rows)
    df = split_location(df)

    out_path = f"{username}-bc-locations.csv"
    df.to_csv(out_path, index=False)
    logging.info(f"Locations saved in {out_path}")


if __name__ == "__main__":
    args = parse_arguments()
    main(args.username)
