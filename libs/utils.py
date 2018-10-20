# -*- coding: utf-8 -*-
import logging
from datetime import datetime


def logger(msg, file):
    """
    Func which logging message into file.
    :param msg:
    :param file:
    :return:
    """
    logger = logging.getLogger('Main')
    logger.setLevel(logging.INFO)

    fh = logging.FileHandler(file)
    fmt = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    formatter = logging.Formatter(fmt)
    fh.setFormatter(formatter)
    logger.addHandler(fh)
    logger.info(msg)


def values_comparison(val1, val2):
    """
    Func which comparison values and return tuple.
    :param val1:
    :param val2:
    :return:
    """
    return (val1, val2) if val1 < val2 else (val1, val2 + 1)


def split_on_ranges(num, num_ranges, btt_specified=1):
    """
    Func which split number on list of ranges.
    :param num: Number which need split on ranges.
    :param num_ranges: Number of ranges on which need to split number.
    :param btt_specified: Just btt specified param. Need for get correct page num.
    :return:
    """
    last_range = num % num_ranges
    ranges_lst = []

    a = ((num - last_range) / num_ranges * btt_specified).__round__()
    c = a

    for i in range(num_ranges):
        e = 0 if i == 0 else btt_specified
        ranges_lst.append((c - a + e, c))

        if i == num_ranges - 1 and last_range != 0:
            ranges_lst.append(values_comparison(c + btt_specified, c + last_range * btt_specified))

        else:
            c += a

    return ranges_lst


def list_creator_of_today_data(titles, links, dates):
    """
    Func which create dict/s of today data from 3 sequences (titles, links, dates).
    :param titles:
    :param links:
    :param dates:
    :return:
    """
    today = datetime.today().strftime('%B %d, %Y').zfill(2)
    finish_lst = []

    for date in dates:
        if today in date:
            index = dates.index(date)

            title = titles.pop(index)
            link = links.pop(index)
            date = dates.pop(index)

            finish_lst.append(dict([('title', title), ('link', link), ('date', date)]))

    return finish_lst
