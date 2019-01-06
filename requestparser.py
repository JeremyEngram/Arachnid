import mimetypes
import urlparser
from scraper import Scraper

def _get_matching_element(a, b):
    for x in a:
        for y in b:
            if x == y:
                return x
    return None

class DocumentRequest:
    def __init__(self, request, applicable_types):
        self.request = request
        self.applicable_types = applicable_types

    def extract(self):
        data = dict()
        data["name"] = self._get_filename() 
        data["code"] = self.request.status_code
        possible_extensions = [t.lstrip(".") for t in mimetypes.guess_all_extensions(self.request.headers["content-type"])]
        data["type"] = _get_matching_element(self.applicable_types, possible_extensions)
        if data["type"]:
            return data 
        return None

    def _get_filename(self):
        try:
            cd = self.request.headers["content-disposition"]
            f_s = cd.find("filename") + 10  # Get index after filename="
            f_e = cd.find("\"", f_s)
            return cd[f_s:f_e]
        except KeyError:
            path = urlparser.parse_url(self.request.url).path
            return path.split("/")[-1]

class HTMLRequest:
    def __init__(self, request, config):
        self.request = request
        self.config = config

    def extract(self):
        data = dict()
        page_contents = Scraper(self.request.text, "html.parser")
        if (self.config.scrape_email):
            data["email"] = page_contents.find_all_emails()
        if (self.config.scrape_phone_number):
            data["phone"] = page_contents.find_all_phones()
        if (self.config.scrape_social_media):
            data["social"] = page_contents.find_all_social()
        if (self.config.custom_str):
            if self.config.custom_str_case_sensitive:
                data["custom_string_occurances"] = page_contents.string_occurances(self.config.custom_str, case_sensitive=True)
            else:
                data["custom_string_occurances"] = page_contents.string_occurances(self.config.custom_str, case_sensitive=False)
        if (self.config.custom_regex):
            data["custom_regex"] = page_contents.find_all_regex(self.config.custom_regex)
        data["code"] = self.request.status_code
        return data
