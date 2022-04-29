import os
import logging
from joblib import dump
from time import time
from HausFinder.utils import local_load_dot_env, check_internet_connection, time_in_mins
from HausFinder.scraper import WebDriver, EbayKlein

env = local_load_dot_env(path=os.environ.get("dotenv_path"))


def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="[%(asctime)s] [%(levelname)s] %(message)s",
    )

    begin = time()
    logging.info("Search script started!")

    if check_internet_connection() != "OK: 200":
        raise RuntimeError("No connection to the internet!!")

    web_driver = WebDriver(driver_path=env["driver_path"])

    # initialise the ebay search engine
    ebay_handler = EbayKlein(
        location=env["search_location"],
        radius=env["search_radius"],
        base_url=env["base_url"],
        category_code=env["cat_code"],
        web_driver=web_driver.session,
    )

    # get advert urls
    logging.info(
        f"Searching in {env['search_radius']} km from {env['search_location']}!"
    )
    advert_urls = ebay_handler.get_advert_urls()
    adverts = ebay_handler.parse_adverts(advert_urls)
    dump(adverts, "adverts_test.joblib")
    # # ebay_handler.filter_bad_adverts()

    # logging.info(f"Search Script finished in {time_in_mins(time()- begin)} minutes")


if __name__ == "__main__":
    main()
