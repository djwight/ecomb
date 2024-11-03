<img src="misc/proj-symbol.png" width="130" title="Citrus myrtifolia" align="right">

# eComb- Haus and Wohnung Finder
A codebase for scraping house or apartment listings from [ebay kleinanzeigen](https://www.ebay-kleinanzeigen.de/) and [Ohne-makler](https://www.ohne-makler.net/) from the current day. 

This can be run locally (with or without docker) or scheduled to run each day on a server to get the listings emailed to interested parties.

## Getting Started

### Prerequisites
Set up a gmail email account to send the listing notifications. Once the account is set up [create an app password](https://support.google.com/accounts/answer/185833) for later use with the script.


Clone the repository locally onto the machine where it will used:

```bash
git clone https://github.com/djwight/ecomb.git
```

### Environment Definition
Variables used at runtime are defined in a `.env` file. 

A dummy `.env` is shown below and how to determine the `base_url` and the `cat_code`.

```bash
email_token="secret-token"
sender="bot@gmail.com"
recipients="email1@email.com;email2@email.de"
search_location="hamburg"
search_radius="10"
driver_path="/usr/local/bin/chromedriver"
base_url="https://www.ebay-kleinanzeigen.de/s-haus-kaufen"
cat_code="c208l3331"
```

To find the `base_url` and the `cat_code` go onto [ebay kleinanzeigen](https://www.ebay-kleinanzeigen.de/) and perform the search you would like to repeat daily. 

For example for "Eigentumswohnung" in Hamburg the url shown would be https://www.ebay-kleinanzeigen.de/s-wohnung-kaufen/hamburg/c196l9409r20, where: 
`https://www.ebay-kleinanzeigen.de/s-wohnung-kaufen` = `base_url` 
`c196l9409` = `cat_code`
`r20` = r + radius (in km) for the search

### Run with docker (recommended)
Create the `.env` as described above and note the absolute path to the directory.

```bash
# moved into dir and build image
cd ecomb
docker build -t <name> .

# once built the container can be run on command or add to crontab to be run each day
docker run -e dotenv_path=/app/data/.env -v </absolute/path/to/dir/with/.env>:/app/data --shm-size="2g" <name>:latest
```

### Run without docker (not recommended)

To run this script locally you will need [chrome](https://www.google.com/chrome/) and the appropriate version of the [chromedriver](https://chromedriver.chromium.org/downloads).
```bash
# activate a new environment with python 3.10 installed and move to the local git repository
cd ecomb
pip install -r requirements.txt

# create an .env and fill out as described above
touch .env

# run the script
export dotenv_path="/path/to/.env"
python3 run_search.py
```

## To-do
- **Ohne-makler**: implement the code to scrape adverets from this site
- **tests**: implement more unit and integration tests
- **documentation**: add documentation