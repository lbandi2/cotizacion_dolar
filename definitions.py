from bs4 import BeautifulSoup
import requests
from db import add_records
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

SPREADSHEET = os.getenv('SPREADSHEET')

class Price:
    def __init__(self, url, utf8=True):
        self.url = url
        self.service_file = 'service.json'
        self.currency = None
        self.name = None
        self.html = self.get_webpage(utf8)
        self.grab_dates()

    def grab_dates(self):
        self.fulldate = datetime.now().strftime("%d/%m/%Y (%H:%M:%S)")
        self.date = datetime.now().strftime("%d/%m/%Y")
        self.timestamp = datetime.now().time()
        self.datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def webpage_is_valid(self, validation_string):
        html = BeautifulSoup(self.html, "html.parser")
        filtered = html.find_all(validation_string)
        if filtered:
            return True
        return False

    def get_webpage(self, utf8):
        try:
            html = requests.get(self.url)
            print("Successfully loaded webpage..")
            if utf8:
                return html.content.decode("utf8")
            return html.content
        except requests.exceptions.ConnectionError:
            print("Invalid URL or internet connection is not working.")
            return None

    def validate_results(self):
        if self.compra and self.venta:
            return True
        return False

    def insert_to_db(self):
        if self.validate_results():
            new_record = {}
            new_record["datetime"] = self.datetime
            new_record["currency"] = self.currency
            new_record["name"] = self.name
            new_record["buy"] = self.compra
            new_record["sell"] = self.venta
            new_record["other"] = self.tarjeta
            if self.validate_results():
                add_records(new_record)
                print("Values written successfully.\n")
        else:
            print("Sorry, can only write values that are valid.\n")


class COP(Price):
    def __init__(self, url):
        print("Loading values for COP..")
        super().__init__(url)
        self.currency = "cop"
        self.name = "generic"
        self.validation_string = "span", {"class": "h1"}
        self.main()

    def main(self):
        self.parse_webpage()
        self.insert_to_db()

    def parse_webpage(self):
        html = BeautifulSoup(self.html, "html.parser")
        if self.webpage_is_valid(self.validation_string):
            filtered = html.find_all("span", {"class": "h1"})

            for index, x in enumerate(filtered):
                value = x.text.split("$ ")[1].replace(",", "")
                if index == 0:
                    self.tarjeta = value
                if index == 1:
                    self.compra = value
                if index == 2:
                    self.venta = value
            print("Got values from webpage..")
        else:
            print("Webapge is not valid, try another URL.")
            self.compra = self.venta = self.tarjeta = self.grab_date = None

class ARSSantander(Price):
    def __init__(self, url):
        print("Loading values for ARS Santander..")
        super().__init__(url, utf8=False)
        self.currency = "ars"
        self.name = "santander"
        self.validation_string = "td"
        self.main()

    def main(self):
        self.parse_webpage()
        self.insert_to_db()

    def parse_webpage(self):
        html = BeautifulSoup(self.html, "html.parser")
        filtered = html.find_all("td")
        self.compra = None
        if self.webpage_is_valid(self.validation_string):
            if filtered:
                for index, x in enumerate(filtered):
                    if x != 'Dólar' or x != 'Euro':
                        if x.text != '$ null':
                            if index == 1:
                                self.compra = float("%.2f" % float(x.text.lstrip().rstrip().split(" ")[1].replace(",", ".")))
                            if index == 2:
                                self.venta = float("%.2f" % float(x.text.lstrip().rstrip().split(" ")[1].replace(",", ".")))
                                self.tarjeta = float("%.2f" % float(self.venta * 1.75))
                            if self.compra is not None:
                                print("Got values from webpage..")
            else:
                print("Webapge is not valid, try another URL.")
                self.compra = self.venta = self.tarjeta = self.grab_date = None

class ARSBNA(Price):
    def __init__(self, url):
        print("Loading values for ARS BNA..")
        super().__init__(url)
        self.currency = "ars"
        self.name = "bna"
        self.validation_string = "td"
        self.main()

    def main(self):
        self.parse_webpage()
        self.insert_to_db()

    def parse_webpage(self):
        html = BeautifulSoup(self.html, "html.parser")
        filtered = html.find_all("td")

        if filtered:
            for index, x in enumerate(filtered):
                if 0 < index < 3:
                    num = x.text.split(",")[0]
                    dec = x.text.split(",")[1]
                    number = f"{num}.{dec}"
                    if index == 1:
                        self.compra = float("%.2f" % float(number))
                    if index == 2:
                        self.venta = float("%.2f" % float(number))
                        self.tarjeta = float("%.2f" % float(self.venta * 1.75))
            print("Got values from webpage..")
        else:
            print("Webapge is not valid, try another URL.")
            self.compra = self.venta = self.tarjeta = self.grab_date = None

class ARSBBVA(Price):
    def __init__(self, url):
        print("Loading values for ARS BBVA..")
        super().__init__(url)
        self.currency = "ars"
        self.name = "bbva"
        self.validation_string = "td", {"class": "number"}
        self.main()

    def main(self):
        self.parse_webpage()
        self.insert_to_db()

    def parse_webpage(self):
        html = BeautifulSoup(self.html, "html.parser")
        filtered = html.find_all("td", {"class": "number"})

        if filtered:
            for index, x in enumerate(filtered):
                num = x.text.split(",")[0].replace("$", "")
                dec = x.text.split(",")[1][0:-1]
                number = f"{num}.{dec}"

                if index == 0:
                    self.compra = float("%.2f" % float(number))
                if index == 1:
                    self.venta = float("%.2f" % float(number))
                    self.tarjeta = float("%.2f" % float(self.venta * 1.75))
            print("Got values from webpage..")
        else:
            print("Webapge is not valid, try another URL.")
            self.compra = self.venta = self.tarjeta = self.grab_date = None

class ARSDolarBlue(Price):
    def __init__(self, url):
        print("Loading values for ARS Dolar Blue..")
        super().__init__(url)
        self.currency = "ars"
        self.name = "blue"
        self.validation_string = "div", {"class": "val"}
        self.main()

    def main(self):
        self.parse_webpage()
        self.insert_to_db()

    def parse_webpage(self):
        html = BeautifulSoup(self.html, "html.parser")
        filtered = html.find_all("div", {"class": "val"})

        if filtered:
            for index, x in enumerate(filtered):
                if '.' in x.text:
                    num = x.text.split(".")[0].replace("$", "")
                    dec = x.text.split(".")[1][0:-1]
                    number = f"{num}.{dec}"
                else:
                    number = x.text.replace("$", "")
                if index == 0:
                    self.compra = float("%.2f" % float(number))
                if index == 1:
                    self.venta = float("%.2f" % float(number))
                    self.tarjeta = 0
            print("Got values from webpage..")
        else:
            print("Webapge is not valid, try another URL.")
            self.compra = self.venta = self.tarjeta = self.grab_date = None

# URL_BLUE = "https://dolarhoy.com"
# a = ARSDolarBlue(URL_BLUE)
# print(a.compra)
# print(a.venta)