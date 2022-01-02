import requests
from bs4 import BeautifulSoup as bs


class EbayKlein:
    header = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.3"
    }

    def __init__(
        self,
        location: str,
        radius: int,
        base_url: str = f"https://www.ebay-kleinanzeigen.de/s-haus-kaufen",
        category_code: str = "c208l3331",
    ) -> None:
        self.final_url = f"{base_url}/{location}/{category_code}r{radius}"

    def get_adverts(self) -> list[str]:
        adverts = []

        # get adverts from last 10 pages
        for i in range(10):
            if i == 0:
                url = self.final_url

            # add site number for next pages
            else:
                url = self.final_url.split("/")
                url = (
                    url[0]
                    + "//"
                    + ("/").join([url[2], url[3], url[4], f"seite:{i+1}", url[5]])
                )
            # make request and parse html
            req = requests.get(url, headers=self.header)
            soup = bs(req.text, "html.parser")

            # collect full address for each advert found
            adverts.extend(
                [
                    "https://www.ebay-kleinanzeigen.de" + link.get("data-href")
                    for link in soup.find_all("article")
                    # if "Heute"
                    # in link.find(
                    #     "div", {"class": "aditem-main--top--right"}
                    # ).text.strip()
                ]
            )
        return adverts

    def parse_advert(self, url: str) -> list[str]:
        req = requests.get(url, headers=self.header)
        soup = bs(req.text, "html.parser")

        price_location = soup.find("div", id="viewad-main-info")
        price = ("preis", price_location.find("h2", id="viewad-price").text.strip())
        location = (
            "ort",
            price_location.find("span", id="viewad-locality").text.strip(),
        )

        summary_details = [
            tuple(i.text.strip().replace(" ", "").split("\n"))
            for i in soup.find("div", id="viewad-details").find_all("li")
        ]
        description = soup.find("p", id="viewad-description-text").text.strip()
        return price, location, summary_details, description
