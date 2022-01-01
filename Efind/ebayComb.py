class Ebay:
    def __init__(
        self,
        location: str,
        radius: int,
        base_url: str = f"https://www.ebay-kleinanzeigen.de/s-haus-kaufen",
        category_code: str = "c208l3331",
    ):
        self.final_url = f"{base_url}/{location}/{category_code}r{radius}"
