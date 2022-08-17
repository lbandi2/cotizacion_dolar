from bs4 import BeautifulSoup
import requests
import re
# from db import add_records
from db import DB
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

class Price:
    def __init__(self, url, tarjeta_comission=0, utf8=True):
        self.url = url
        self.currency = None
        self.name = None
        self.tarjeta_comission = tarjeta_comission
        print(f"\nLoading values for {self.__class__.__name__}..")
        self.compra = None
        self.venta = None
        self.tarjeta = None
        self.html = self.get_webpage(utf8)
        self.grab_dates()

    def grab_dates(self):
        self.fulldate = datetime.now().strftime("%d/%m/%Y (%H:%M:%S)")
        self.date = datetime.now().strftime("%d/%m/%Y")
        self.timestamp = datetime.now().time()
        # self.datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.datetime = datetime.now()

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
        new_record = {}
        new_record["datetime"] = self.datetime
        new_record["currency"] = self.currency
        new_record["name"] = self.name
        new_record["buy"] = self.compra
        new_record["sell"] = self.venta
        new_record["other"] = self.tarjeta
        if self.validate_results():
            db = DB(self.currency, self.name)
            db.add_records(new_record)
        else:
            print(f"Sorry, can only write values that are valid.\nCurrent values: {new_record}")


class COP(Price):
    def __init__(self, url):
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
                    self.tarjeta = float("%.2f" % float(value))
                if index == 1:
                    self.compra = float("%.2f" % float(value))
                if index == 2:
                    self.venta = float("%.2f" % float(value))
            print("Got values from webpage..")
        else:
            print("Webapge is not valid, try another URL.")
            self.compra = self.venta = self.tarjeta = self.grab_date = None

class ARSSantander(Price):
    def __init__(self, url, tarjeta_comission):
        super().__init__(url, tarjeta_comission, utf8=False)
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
                                self.tarjeta = float("%.2f" % float(self.venta * self.tarjeta_comission))
                if self.compra is not None:
                    print("Got values from webpage..")
            else:
                print("Webapge is not valid, try another URL.")
                self.compra = self.venta = self.tarjeta = self.grab_date = None

class ARSPatagonia(Price):
    def __init__(self, url, tarjeta_comission):
        super().__init__(url, tarjeta_comission, utf8=False)
        self.currency = "ars"
        self.name = "patagonia"
        self.validation_string = "tr", {"class": "odd"}
        self.main()

    def main(self):
        self.parse_webpage()
        self.insert_to_db()

    def parse_webpage(self):
        html = BeautifulSoup(self.html, "html.parser")
        filtered = html.find_all("tr", {"class": "odd"})
        self.compra = None
        self.venta = None
        if self.webpage_is_valid(self.validation_string):
            if filtered:
                for index, x in enumerate(filtered):
                    match = re.search("\d{3,5}(,|.)\d{1,2}", x.text).group()
                    value = match.replace(",", ".")
                    if value != '$ null':
                        if self.compra is None:
                            self.compra = float("%.2f" % float(value))
                        if self.venta is None:
                            self.venta = float("%.2f" % float(value))
                            self.tarjeta = float("%.2f" % float(self.venta * self.tarjeta_comission))
                if self.compra is not None:
                    print("Got values from webpage..")
            else:
                print("Webapge is not valid, try another URL.")
                self.compra = self.venta = self.tarjeta = self.grab_date = None


class ARSBNA(Price):
    def __init__(self, url, tarjeta_comission):
        super().__init__(url, tarjeta_comission)
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
                        self.tarjeta = float("%.2f" % float(self.venta * self.tarjeta_comission))
            print("Got values from webpage..")
        else:
            print("Webapge is not valid, try another URL.")
            self.compra = self.venta = self.tarjeta = self.grab_date = None

class ARSBBVA(Price):
    def __init__(self, url, tarjeta_comission):
        super().__init__(url, tarjeta_comission)
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
                    self.tarjeta = float("%.2f" % float(self.venta * self.tarjeta_comission))
            print("Got values from webpage..")
        else:
            print("Webapge is not valid, try another URL.")
            self.compra = self.venta = self.tarjeta = self.grab_date = None

class ARSDolarBlue(Price):
    def __init__(self, url):
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


if __name__ == '__main__':
    URL_BLUE = "https://dolarhoy.com"
    a = ARSDolarBlue(URL_BLUE)
    print(a.compra)
    print(a.venta)
    # URL_COP = "https://www.dolarhoy.co"
    # a = COP(URL_COP)
    # print(a.compra)

    # URL_PATAGONIA = "https://ebankpersonas.bancopatagonia.com.ar/eBanking/usuarios/cotizacionMonedaExtranjera.htm"
    # a = ARSPatagonia(URL_PATAGONIA)
    # a.compra
    # a.venta
