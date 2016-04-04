import asyncio
import json
from datetime import datetime
from helper.filter import remove_emoji

import lxml.html

from speaker.play import REGIONS
from helper.http_client import user_agent, request


@asyncio.coroutine
def latest_reviews(code, region, buffer_size):
    lang = REGIONS[region]['lang']
    url = 'https://play.google.com/store/getreviews?hl={}'.format(lang)
    headers = {
        'User-Agent': user_agent(),
        'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8'
    }
    payload = {
        'reviewType': 0,
        'pageNum': 0,
        'id': code,
        'reviewSortOrder': 0,
        'xhr': 1
    }
    body = yield from request(url, headers=headers, payload=payload)
    raw_reviews = remove_emoji(json.loads(body.decode('utf-8').replace(")]}'", "").strip())[0][2])
    tree = lxml.html.fromstring(raw_reviews)
    reviews = list()
    for raw_review in tree.xpath('//div[@class="single-review"]')[:buffer_size]:
        reviews.append({
            'id': raw_review.xpath('./div[@class="review-header"]')[0].attrib['data-reviewid'],
            'title': raw_review.xpath('./div[@class="review-body with-review-wrapper"]/span[@class="review-title"]')[0].text,
            'content': raw_review.xpath('./div[@class="review-body with-review-wrapper"]')[0].text_content().replace(raw_review.xpath('./div/div[@class="review-link"]')[0].getchildren()[0].text, '').strip(),
            'name': raw_review.xpath('./div[@class="review-header"]/div[@class="review-info"]/span/a')[0].text_content(),
            'score': int(raw_review.xpath('./div/div/div/div/div[@class="current-rating"]')[0].attrib['style'].replace('width:', '').replace('%', '').replace(';', '').strip()),
            'date': date(region, raw_review.xpath('./div/div/span[@class="review-date"]')[0].text),
            'version': None,
            'lang': lang,
            'region': region
        })
    return reviews


def date(country, raw_date):
    store = REGIONS[country]
    if store['lang'] == 'th':
        # Ex) 1 กุมภาพันธ์ 2558 -> 1 2 2015
        raw_date = thai_date(raw_date)
    return datetime.strptime(raw_date, store['date_format'])


def thai_date(raw_date):
    raw_date = raw_date.replace('มกราคม', '1')
    raw_date = raw_date.replace('กุมภาพันธ์', '2')
    raw_date = raw_date.replace('มีนาคม', '3')
    raw_date = raw_date.replace('เมษายน', '4')
    raw_date = raw_date.replace('พฤษภาคม', '5')
    raw_date = raw_date.replace('มิถุนายน', '6')
    raw_date = raw_date.replace('กรกฎาคม', '7')
    raw_date = raw_date.replace('สิงหาคม', '8')
    raw_date = raw_date.replace('กันยายน', '9')
    raw_date = raw_date.replace('ตุลาคม', '10')
    raw_date = raw_date.replace('พฤศจิกายน', '11')
    raw_date = raw_date.replace('ธันวาคม', '12')

    thailand_year_diff = 543
    thailand_year = raw_date.split(' ')[2]
    year = str(int(thailand_year) - thailand_year_diff)
    return raw_date.replace(thailand_year, year)
