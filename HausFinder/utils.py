import requests
import logging
import numpy as np


def time_in_mins(secs: int, dp: int = 2) -> float:
    """Returns seconds as minutes.

    Args:
        secs (int): Seconds to convert to minutes
        dp (int, optional): Decimal places of the minutes float to return. Defaults to 2.

    Returns:
        float: secs as minutes
    """
    return np.round(secs / 60, dp)


def check_internet_connection() -> str:
    """Checks connection to the internet by using google.de as a proxy.

    Returns:
        str: status and status code from request to google.de
    """
    req = requests.get("https://www.google.de/")
    if status := req.status_code == 200:
        logging.info("Internet connected!")
        return "OK: 200"
    else:
        logging.error(f"No internet connection, Error {status}")
        return f"ERROR: {status}"
