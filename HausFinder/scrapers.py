import logging
from typing import List, Type, Dict
from random import uniform
import datetime
from time import time, sleep
from bs4 import BeautifulSoup as bs
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from HausFinder.utils import time_in_mins


class WebDriver:
    """Generates an instance of a chromewedriver for use with selenium for website scraping.

    Args:
        driver_path (str): path to chromedriver
    """

    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")

    def __init__(self, driver_path: str) -> None:
        self.session = webdriver.Chrome(driver_path, options=self.options)

    def driver_quit(self) -> None:
        logging.info("Chrome session shutingdown...")
        self.session.quit()


class EbayKlein:
    """Class for scraping and cleaning Haus or Wohnung adverts from Ebay Kleinanzeigen.

    Args:
        location (str): location of the search (must match the what is on the website)
        radius (str): radius from location for the search
        base_url (str): the base url on Ebay kleinanzeigen
        category_code (str): each category and location has a query string code (find online based on the base_url and location)
        web_driver (Type[WebDriver]): initialized instance of the chrome webdriver for scraping with selenium
    """

    def __init__(
        self,
        location: str,
        radius: str,
        base_url: str,
        category_code: str,
        web_driver: Type[WebDriver],
    ) -> None:
        self.location = location
        self.radius = radius
        self.base_url = base_url
        self.category_code = category_code
        self.final_url = f"{base_url}/{location}/{category_code}r{radius}"
        self.session = web_driver
        self.connection = self._test_klein_connection()

    @staticmethod
    def delay_random(low: float, high: float) -> None:
        """Delay further execution of code by a random length of time (low>= delay (s) <= high).

        Args:
            low (float): minimum seconds to delay
            high (float): maximum seconds to delay
        """
        delay = uniform(low, high)
        sleep(delay)

    def get_advert_urls(self) -> List[str]:
        """Scrape Ebay Kleinanzeigen for all of the adverts in the search category that were posted today (i.e. "Heute").

        Returns:
            List[str]: list of urls matching the search criteria
        """
        urls = [
            self.final_url
            if idx == 0
            else f"{self.base_url}/{self.location}/seite:{idx+1}/{self.category_code}r{self.radius}"
            for idx in range(5)
        ]
        advert_urls = []
        for url in urls:
            logging.info(f"Scraping URLs from: {url}")
            try:
                self.session.get(url)
                element_waited = ec.presence_of_element_located(
                    (By.ID, "consentBanner")
                )
                WebDriverWait(self.session, timeout=10).until(element_waited)
            except TimeoutException:
                logging.warning(f"{url} did not load!! Skipping!")
                continue

            # collect full address for each advert found
            soup = bs(self.session.page_source, "lxml")
            advert_urls.extend(
                [
                    "https://www.ebay-kleinanzeigen.de" + link.get("data-href")
                    for link in soup.find_all("article")
                    if "Gestern"
                    in link.find("div", class_="aditem-main--top--right")
                    .get_text()
                    .strip()
                ]
            )
            # random rate limit to prevent failed requests from spamming
            self.delay_random(0.2, 1.5)

        advert_urls = list(set(advert_urls))  # remove dups
        logging.info(f"{len(advert_urls)} advert URLs found!")
        return advert_urls

    def parse_adverts(self, advert_urls: List[str]) -> List[Dict[str, str]]:
        """Parses the data from the individual adverts using a list of advert urls. Re-tries failed
        adverts up to 6 times before logging their failure.

        Args:
            advert_urls (List[str]): urls of the adverts to parse

        Returns:
            List[Dict[str, str]]: list of dictionaries containing the parsed advert data
        """
        begin = time()
        logging.info(f"Parsing {(n_adverts:=len(advert_urls))} adverts!")

        adverts, failed = [], []
        count = 1
        for url in advert_urls:
            try:
                self.session.get(url)
                element_waited = ec.presence_of_element_located(
                    (By.ID, "viewad-description-text")
                )
                WebDriverWait(self.session, timeout=20).until(element_waited)
            except TimeoutException:
                logging.warning(f"{url} did not load!! Skipping URL!")
                failed.append(url)
                continue

            adverts = self._parse_advert(url, adverts)

            # random rate limit to prevent failed requests
            self.delay_random(0.1, 1.2)

            logging.info(f"{count}/{len(advert_urls)} urls done in first round!")
            count += 1

        logging.info(
            f"FIRST ROUND: Parsed {len(adverts)} in {time_in_mins(time()-begin)} minutes"
        )
        logging.info(f"FIRST ROUND: {len(failed)} failed URLs being re-tried!")

        parse_round = 1
        while (len(failed) > 0) or (parse_round < 6):
            for failed_url in failed:
                try:
                    self.session.get(failed_url)
                    element_waited = ec.presence_of_element_located(
                        (By.ID, "viewad-description-text")
                    )
                    WebDriverWait(self.session, timeout=20).until(element_waited)
                except TimeoutException:
                    continue

                logging.info(
                    f"Round {parse_round}: {failed_url} sorted in repeat round"
                )
                adverts = self._parse_advert(failed_url, adverts)
                failed.remove(failed_url)
                logging.info(f"{len(failed)} URLs remain to be resolved!")

                # rate limit requests if they are fast (max 2/s)
                self.delay_random(0.1, 1.2)

            parse_round += 1

        logging.warning(f"{len(failed)} failed URLs not loaded after 5 attempts!")
        logging.warning(f"Failed URLs: {failed}")
        return adverts

    def filter_bad_adverts(
        self, adverts: List[Dict[str, str]], search_prefs: Dict[str, str]
    ) -> List[Dict[str, str]]:
        # remove adverts with no text description
        logging.info(f"{len(adverts)} input adverts to be filtered!")
        filtered = [i for i in adverts if i["description"] != ""]
        logging.info(
            f"{len(adverts)- (num_remain:=len(filtered))} removed as have no description: {num_remain} remaining"
        )

        # remove postings older than 24h (intended to be run at midnight)
        yesterday = datetime.datetime.strftime(
            (datetime.date.today() - datetime.timedelta(days=1)), "%d.%m.%Y"
        )
        filtered = [i for i in adverts if i["posted"] == yesterday]

        return

    def _test_klein_connection(self) -> None:
        """Tests connection to the final_url at ebaykleinanzeigen.

        Raises:
            RuntimeError: caused by failure with any 4xx or 5xx error
        """
        req = requests.get(
            self.final_url,
            headers={
                "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.3"
            },
        )

        # return status connection code
        if (status := req.status_code) >= 400:
            logging.error(
                (
                    msg := f"Connection to Ebay Kleinanzeigen not possible! Status code: {status}"
                )
            )
            raise RuntimeError(msg)
        else:
            logging.info(
                f"Connection to Ebay kleinanzeigen successful with status code: {status}!"
            )

    def _parse_advert(
        self, url: str, adverts: List[Dict[str, str]]
    ) -> List[Dict[str, str]]:
        """Parses important information form a single advert url.

        Args:
            url (str): url for advert to be parsed
            adverts (List[Dict[str, str]]): current list of parsed adverts

        Returns:
            List[Dict[str, str]]: current list of parsed adverts with the latest appended
        """
        soup = bs(self.session.page_source, "lxml")
        top_info = soup.find("div", id="viewad-extra-info")
        if top_info is None:
            print(soup)

        date_posted = top_info.find("span").text

        price_location = soup.find("div", id="viewad-main-info")
        price = price_location.find("h2", id="viewad-price").text.strip()
        location = price_location.find("span", id="viewad-locality").text.strip()
        title = soup.find("h1", id="viewad-title").text.strip().split("\n")[-1].strip()

        if soup.find("div", id="viewad-details") is None:
            summary_details = None
        else:
            summary_details = dict(
                [
                    tuple(i.text.strip().replace(" ", "").split("\n"))
                    for i in soup.find("div", id="viewad-details").find_all("li")
                ]
            )

        description = soup.find("div", id="viewad-description").get_text().strip()

        adverts.append(
            {
                "posted": date_posted,
                "price": price,
                "location": location,
                "title": title,
                "url": url,
                "summary_details": summary_details,
                "description": description,
            }
        )
        return adverts


class OhneMakler:
    def __init__(self) -> None:
        raise NotImplementedError("OhneMakler.net not yet implemented!")
