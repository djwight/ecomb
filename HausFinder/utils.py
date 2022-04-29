import requests
import logging
from typing import Dict
import numpy as np


def local_load_dot_env(path: str) -> Dict[str, str]:
    """Loads env variables from a.env file without entering these into the container environment.

    Args:
        path (str): path to .env file

    Returns:
        Dict[str, str]: dict with env variable name as keys and values as the items
    """
    with open(path, "r") as f:
        return dict(
            tuple(line.replace("\n", "").replace('"', "").split("="))
            for line in f.readlines()
            if not line.startswith("#")
        )


def time_in_mins(secs: int, dp: int = 2) -> np.float64:
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
