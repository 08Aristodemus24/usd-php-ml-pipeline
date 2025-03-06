from dateutil import parser
import datetime as dt

def reformat_date(date: dt.datetime):
    datetime_obj = parser.parse(date)
    year = datetime_obj.year
    month = datetime_obj.month
    day = datetime_obj.day
    combined_date = f'{day} {month} {year}'

    # this is the format we need to use if we are going to make
    # api requests to polygon api
    reformed_date = dt.datetime.strptime(combined_date, '%d %m %Y').strftime('%Y-%m-%d')

    return reformed_date