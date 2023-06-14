# Bandcamp City Scraper 🎵🌇

A very simple tool to extract the locations of artists/labels in a given bandcamp collection and format them into a table for location -> artist/label searching. Trying to answer the question: "Hey I'm in X city, are there any artist/labels I'm interested in who are based here?".

**NOTE:** a much more comprehensive bandcamp metadata extractor can be found here: [bandcamp-fetch](https://github.com/patrickkfkan/bandcamp-fetch)

## Installation

With [conda](https://conda.io/projects/conda/en/latest/user-guide/install/index.html)/[miniconda](https://docs.conda.io/en/latest/miniconda.html):

```bash
conda env create -f env.yml
```

## Usage

```bash
conda activate bc-city-scraper
python main.py --username <target bandcamp username>
```

The extracted data will be saved to a `bc-locations.csv` file.

**NOTE:** the request rate to the bandcamp website has been throttled

## Possible future extensions 🔮

- include wishlisted items
- include followed artists/labels
