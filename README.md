# Bandcamp City Scraper 🌇

A very simple tool to extract the locations of artists/labels in my bandcamp collection and format them into a table for location -> artist/label searching. Trying to answer the question: "Hey I'm in X city, are there any artist/labels I'm interested in who are based here?".

## Installation 

```bash
conda env create -f env.yml
```

## Usage

First modify the `config.yml` file to add your target `username`. This will be the profile where the artists/labels are scraped from.

```bash
conda activate bc-city-scraper
python main.py
```

Then follow the instructions to save the extracted data to a `.csv` file.