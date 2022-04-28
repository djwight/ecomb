import os
import logging
from joblib import dump
from time import time
from HausFinder.utils import check_internet_connection, time_in_mins
from HausFinder.iScrape import WebDriver, EbayKlein

LOCATION = os.environ.get("search_location", "berlin")
RADIUS = os.environ.get("search_radius", "20")
DRIVER_PATH = os.environ.get("driver_path", "/home/darren/Documents/chromedriver")
BASE_URL = os.environ.get("base_url", "https://www.ebay-kleinanzeigen.de/s-haus-kaufen")
CAT_CODE = os.environ.get("cat_code", "c208l3331")


def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="[%(asctime)s] [%(levelname)s] %(message)s",
    )

    begin = time()
    logging.info("Search script started!")

    if check_internet_connection() != "OK: 200":
        raise RuntimeError("No connection to the internet!!")

    web_driver = WebDriver(driver_path=DRIVER_PATH)

    # initialise the ebay search engine
    ebay_handler = EbayKlein(
        location=LOCATION,
        radius=RADIUS,
        base_url=BASE_URL,
        category_code=CAT_CODE,
        web_driver=web_driver.session,
    )

    # get advert urls
    logging.info(f"Searching in {RADIUS} km from {LOCATION}!")
    advert_urls = ebay_handler.get_advert_urls()
    adverts = ebay_handler.parse_adverts(advert_urls)
    dump(adverts, "adverts_test.joblib")
    # # ebay_handler.filter_bad_adverts()

    # logging.info(f"Search Script finished in {time_in_mins(time()- begin)} minutes")


if __name__ == "__main__":
    main()
