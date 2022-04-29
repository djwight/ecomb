import os
import logging
from joblib import dump
from time import time
import datetime
from HausFinder.utils import local_load_dot_env, check_internet_connection, time_in_mins
from HausFinder.scrapers import WebDriver, EbayKlein
from HausFinder.notifications import EmailHandler

env = local_load_dot_env(path=os.environ.get("dotenv_path"))

# parse out multiple recipient emails
env["recipients"] = env["recipients"].split(";")


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

    # initialise the ebay scraping engine
    ebay_handler = EbayKlein(
        location=env["search_location"],
        radius=env["search_radius"],
        base_url=env["base_url"],
        category_code=env["cat_code"],
        web_driver=web_driver.session,
    )

    # get advert urls and parse adverts
    logging.info(
        f"Searching in {env['search_radius']} km from {env['search_location']}!"
    )
    advert_urls = ebay_handler.get_advert_urls()
    adverts = ebay_handler.parse_adverts(advert_urls)
    # dump(adverts, "adverts_test.joblib")
    # # ebay_handler.filter_bad_adverts()

    # create an email handler instance
    emailer = EmailHandler(
        sender_email=env["sender"], receiver_emails=env["recipients"]
    )

    # make email elements
    email_adverts = ("").join(
        f"<p>{a['price']}--<b>{a['title']}</b>--{a['location']}<br>{a['url']}<br><br></p>"
        for a in adverts
    )
    today = datetime.datetime.strftime(datetime.date.today(), "%d.%m.%Y")

    email_text = f"""
    <html>
        <body>
            <p>Hi Bargain Hunter!</p>
            <p>Here are the new adverts from {today}.</p>
            <b> LISTINGS </b>
            {email_adverts}
        </body>
    </html>
    """

    # create emails and send
    emailer.build_email(
        subject=f"Ebay Search in {env['search_location']}: {today}", text=email_text
    )
    emailer.send_email(username=env["sender"], password=env["email_token"])
    emailer.server_quit()

    # logging.info(f"Search Script finished in {time_in_mins(time()- begin)} minutes")
    web_driver.driver_quit()


if __name__ == "__main__":
    main()
