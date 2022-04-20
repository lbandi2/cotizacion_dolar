from bs4 import BeautifulSoup
import requests
from secrets import json_secret
import pygsheets
from datetime import datetime

class Price:
    def __init__(self, url):
        self.url = url
        self.service_file = 'service.json'
        self.google_spreadsheet = json_secret('spreadsheet')
        self.html = self.get_webpage()
        self.grab_dates()
        self.sheet_num = None

    def grab_dates(self):
        self.fulldate = datetime.now().strftime("%d/%m/%Y (%H:%M:%S)")
        self.date = datetime.now().strftime("%d/%m/%Y")
        self.timestamp = datetime.now().time()

    def webpage_is_valid(self, validation_string):
        html = BeautifulSoup(self.html, "html.parser")
        filtered = html.find_all(validation_string)
        if filtered:
            return True
        return False

    def get_webpage(self):
        try:
            html = requests.get(self.url)
            print("Successfully loaded webpage..")
            return html.content.decode("utf8")
        except requests.exceptions.ConnectionError:
            print("Invalid URL or internet connection is not working.")
            return None

    def spreadsheet(self, sheet):
        try:
            google_sheet = pygsheets.authorize(service_file=self.service_file)
            spreadsheet = google_sheet.open_by_key(self.google_spreadsheet)
            working_sheet = spreadsheet[sheet]
            return working_sheet
        except Exception:
            print("Something's wrong with the google service file or wrong spreadsheet.")

    def validate_results(self):
        if self.compra is not None and self.venta is not None and self.tarjeta is not None:
            return True
        return False

    def write_to_spreadsheet(self):
        if self.validate_results():
            sheet_date = self.spreadsheet(self.sheet_num).cell('A2').value
            if sheet_date == self.date:
                self.spreadsheet(self.sheet_num).update_row(index=2, values=[self.date, self.fulldate, self.compra, self.venta, self.tarjeta])
            else:
                self.spreadsheet(self.sheet_num).insert_rows(row=1, number=1, values=[self.date, self.fulldate, self.compra, self.venta, self.tarjeta])
            print("Values written successfully.\n")
        else:
            print("Sorry, can only write values that are valid.\n")


class COP(Price):
    def __init__(self, url):
        print("Loading values for COP..")
        super().__init__(url)
        self.sheet_num = 8
        self.validation_string = "span", {"class": "h1"}
        self.main()

    def main(self):
        self.parse_webpage()
        self.write_to_spreadsheet()

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
        super().__init__(url)
        self.sheet_num = 7
        self.validation_string = "td"
        self.main()

    def main(self):
        self.parse_webpage()
        self.write_to_spreadsheet()

    def get_webpage(self):
        try:
            html = requests.get(self.url)
            print("Successfully loaded webpage..")
            return html.content
        except requests.exceptions.ConnectionError:
            print("Invalid URL or internet connection is not working.")
            return None

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
                                self.tarjeta = float("%.2f" % float(self.venta * 1.65))
                            if self.compra is not None:
                                print("Got values from webpage..")
            else:
                print("Webapge is not valid, try another URL.")
                self.compra = self.venta = self.tarjeta = self.grab_date = None

class ARSBNA(Price):
    def __init__(self, url):
        print("Loading values for ARS BNA..")
        super().__init__(url)
        self.sheet_num = 5
        self.validation_string = "td"
        self.main()

    def main(self):
        self.parse_webpage()
        self.write_to_spreadsheet()

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
                        self.tarjeta = float("%.2f" % float(self.venta * 1.65))
            print("Got values from webpage..")
        else:
            print("Webapge is not valid, try another URL.")
            self.compra = self.venta = self.tarjeta = self.grab_date = None

class ARSBBVA(Price):
    def __init__(self, url):
        print("Loading values for ARS BBVA..")
        super().__init__(url)
        self.sheet_num = 6
        self.validation_string = "td", {"class": "number"}
        self.main()

    def main(self):
        self.parse_webpage()
        self.write_to_spreadsheet()

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
                    self.tarjeta = float("%.2f" % float(self.venta * 1.65))
            print("Got values from webpage..")
        else:
            print("Webapge is not valid, try another URL.")
            self.compra = self.venta = self.tarjeta = self.grab_date = None



