import requests
from bs4 import BeautifulSoup

class HelloCallersAPI:
    def __init__(self, base, cookies_raw, xsrf_token):
        self.base = base.rstrip("/")
        self.session = requests.Session()
        for c in cookies_raw.split(";"):
            if "=" in c:
                k, v = c.strip().split("=", 1)
                self.session.cookies.set(k, v)
        self.default_xsrf = xsrf_token
        self.default_headers = {
            "User-Agent": "Mozilla/5.0",
            "Accept": "application/json, text/plain, */*",
            "Content-Type": "application/json;charset=UTF-8",
            "Referer": self.base + "/",
            "api-version": "2",
            "x-xsrf-token": xsrf_token
        }

    def post(self, path, json=None):
        r = self.session.post(
            self.base + path,
            json=json,
            headers=self.default_headers
        )
        r.raise_for_status()
        return r.json()

    def get_csrf_token(self, number, iso="eg"):
        url = f"{self.base}/user/search?type=number&iso2={iso}&query={number}"
        r = self.session.get(url, headers=self.default_headers)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")
        token_input = soup.find("input", {"name": "_token"})
        if token_input:
            return token_input["value"]
        raise ValueError("CSRF token not found")

    # ----------------------
    # APIs methods
    # ----------------------
    def contact_names(self, contact_id: str):
        return self.post("/user/contact/names", {"id": contact_id})

    def search_contact(self, number: str, iso="eg"):
        token = self.get_csrf_token(number, iso)
        payload = {"iso_code": iso, "contact": number, "_token": token}
        return self.post("/user/search/contact", payload)