# coding: utf-8
import re
import os
import csv
from datetime import datetime, timedelta

import requests
from templater import Templater

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir))
URL = 'http://www.lacumbuca.com/2012/10/em-outubro-no-rio-feist-gossip-gal.html'

class Show():

    def __init__(self, name, date_and_time, price, place):
        self.name = name
        self.price = price
        self.date_and_time = date_and_time
        self.place = place

    @classmethod
    def from_raw_data(cls, raw_data):
        name = raw_data[0]
        price = raw_data[2]
        place = raw_data[4]
        day, month, year = [int(x) for x in raw_data[1].split()[-1].split('/')]
        hour, minute = [int(x) for x in raw_data[3].split()[-1].replace('"', '').split(':')]
        date_and_time = datetime(2000 + year, month, day, hour, minute)
        return cls(name, date_and_time, price, place)

    def __repr__(self):
        return self.name + ' - ' + self.date_and_time.strftime('%d/%m/%Y')

    def to_csv_row(self):
        end_time = self.date_and_time + timedelta(seconds=2 * 60 * 60)
        return [
            self.name,
            self.date_and_time.strftime('%d/%m/%Y'),
            self.date_and_time.strftime('%I:%M:%S %p'),
            end_time.strftime('%d/%m/%Y'),
            end_time.strftime('%I:%M:%S %p'),
            'False',
            self.price,
            self.place,
            'False'
        ]

def get_shows_from_html(html_content):
    regexp_marker = re.compile(r'{{([a-zA-Z0-9_-]*)}}')
    regexp_tags = re.compile(r'<[^>]*?>')
    template_fp = open(os.path.join(PROJECT_ROOT, 'src', 'template.html'))
    template = Templater(template_fp.read().strip(), marker=regexp_marker)
    data = template.parse(html_content)
    shows = []

    for evento in data['info'].split('</blockquote>'):
        raw_show = regexp_tags.sub('', evento).strip().split('\n')
        try:
            shows.append(Show.from_raw_data(raw_show))
        except ValueError:
            pass

    return shows

def main():
    response = requests.get(URL)
    shows = get_shows_from_html(response.content)

    csv_header = 'Subject,Start Date,Start Time,End Date,End Time,All Day Event,Description,Location,Private'
    with open(os.path.join(PROJECT_ROOT, 'calendar.csv'), 'w') as csvfile:
        csv_calendar = csv.writer(csvfile, delimiter=',')
        csv_calendar.writerow(csv_header.split(','))
        for show in shows:
            csv_calendar.writerow(show.to_csv_row())

if __name__ == '__main__':
    main()
