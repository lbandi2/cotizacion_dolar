from datetime import datetime

def date_to_string(date):
    return datetime.strftime(date, "%Y-%m-%d %H:%M:%S")

