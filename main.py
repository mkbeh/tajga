# -*- coding: utf-8 -*-
import time
import re

import requests

from multiprocessing import Process

from bs4 import BeautifulSoup
from torrequest import TorRequest

from libs.pymongodb import pymongodb
from libs import utils
from libs import decorators


class Parser(object):
    def __init__(self):
        self.url = 'https://bitcointalk.org/index.php?board=159.{}'
        self.last_page_num = None
        self.processes_num = 10                                          # Desired number of processes

        self.mongo_ = self.check_on_clear_db()

    @staticmethod
    def check_on_clear_db():
        """
        Method which check database on clear by test find document in collection.
        :return:
        """
        mongo = pymongodb.MongoDB('btt')
        document = mongo.find({}, 'en_altcoins', 1)

        return True if document else False

    @staticmethod
    def get_html(url):
        """
        Method which send GET request to specific url and return html.
        :param url:
        :return:
        """
        time.sleep(3)

        try:
            html = requests.get(url, timeout=(10, 27), stream=True).content
        except Exception as e:
            print(e)

            with TorRequest(proxy_port=9050, ctrl_port=9051, password=None) as tr:
                tr.reset_identity()
                html = tr.get(url, timeout=(10, 27), stream=True).content

        return html

    @staticmethod
    def write_data(**kwargs):
        """
        Method which insert data in specific collection.
        :param kwargs: dict/s of data.
        :return:
        """
        mongo = pymongodb.MongoDB('btt')
        mongo.insert_one(kwargs, 'en_altcoins')

        utils.logger('Data has been written', 'tajga_page_parsed.log')

    def parse_last_page_num(self):
        """
        Method which parse last page number from first page.
        :return:
        """
        bs_obj = BeautifulSoup(self.get_html(self.url.format('0')), 'lxml')
        self.last_page_num = int(bs_obj.findAll('a', {'class': 'navPages'})[-2].get_text())

    def parse_range(self, range_):
        """
        Method which parse range of pages.
        :param range_: range of pages => (0, 80)
        :return:
        """
        count = range_[0]

        while count != (range_[1] + 40):
            print('count', count)
            self.parse(count)
            count += 40

    def parse(self, page_num):
        """
        Method which parse specific page.
        :param page_num: page number
        :return:
        """
        bs_obj = BeautifulSoup(self.get_html(self.url.format(page_num)), 'lxml')

        # Log parse page start.
        utils.logger(f'Parsing {page_num} started.', 'tajga_page_parsed.log')

        # Find specific data.
        posts_links = bs_obj.findAll('span', {'id': re.compile('msg_\d*')})
        titles = [title.find('a').text for title in posts_links]
        links = [link.find('a')['href'] for link in posts_links]

        # Find topics started dates.
        topic_started_dates = []

        for i in range(len(links)):
            post_bs_obj = BeautifulSoup(self.get_html(links[i]), 'lxml')

            # Find topics started dates.
            td = post_bs_obj.find('td', {'class': 'td_headerandpost'})
            topic_started_date = td.find('div', {'class': 'smalltext'}).get_text()
            topic_started_dates.append(topic_started_date)

        # If database is clear or not.
        if self.mongo_:
            data_lst = utils.list_creator_of_today_data(titles, links, topic_started_dates)

            for data_dict in data_lst:
                self.write_data(title=data_dict['title'], link=data_dict['link'], topic_started_date=data_dict['date'])

        else:
            for i in range(len(titles)):
                self.write_data(title=titles[i], link=links[i], topic_started_date=topic_started_dates[i])

    @decorators.log
    def run(self):
        """
        Method which run parser.
        First - parse last page number , then split it on ranges.
        Second - create processes which parse received ranges.
        :return:
        """
        self.parse_last_page_num()                                         # Find last page number.
        self.last_page_num = 100 if self.mongo_ else self.last_page_num    # Set 100 pages for not clear db.
        ranges = utils.split_on_ranges(self.last_page_num, 2, 40)          # Split LPN on ranges.

        # Parse pages by ranges in own process.
        [Process(target=self.parse_range, args=(range_,)).start() for range_ in ranges]


if __name__ == '__main__':
    try:
        Parser().run()
    except:
        utils.logger('Success status: %s' % 'ERROR', 'tajga.log')
