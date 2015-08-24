import asyncio
from helper.filter import remove_emoji
from helper.lang import find_out_language
from lxml import etree
from datetime import datetime
from helper.http_client import request
from speaker.appstore import NAMESPACE, REGIONS


@asyncio.coroutine
def latest_reviews(code, region, buffer_size):
    url = "http://ax.phobos.apple.com.edgesuite.net/WebObjects/MZStore.woa/wa/viewContentsUserReviews?id={}&pageNumber={}&sortOrdering=4&onlyLatestVersion=false&type=Purple+Software".format(code, 0)
    headers = {
        'X-Apple-Store-Front': REGIONS[region]['app_store_id'],
        'User-Agent': 'iTunes/9.2 (Macintosh; U; Mac OS X 10.6)'
    }
    body = yield from request(url, headers=headers)
    reviews = list()
    for raw_review in etree.XML(body).xpath('//ns:VBoxView[@leftInset="10"]', namespaces=NAMESPACE)[1:][:buffer_size]:
        review_info = raw_review.xpath('./ns:HBoxView', namespaces=NAMESPACE)[1].xpath(
            './ns:TextView[@topInset="0"]/ns:SetFontStyle/ns:GotoURL', namespaces=NAMESPACE)[0].tail.split('-')
        title = raw_review.xpath('./ns:HBoxView[@bottomInset="3"]/ns:TextView/ns:SetFontStyle/ns:b', namespaces=NAMESPACE)[0].text
        content = raw_review.xpath('./ns:TextView[@topInset="2"]/ns:SetFontStyle', namespaces=NAMESPACE)[0].text
        reviews.append({
            'id': raw_review.xpath('./ns:HBoxView[@bottomInset="3"]/ns:HBoxView[@stretchiness="1"]/ns:HBoxView[@rightInset="0"]/ns:VBoxView/ns:GotoURL', namespaces=NAMESPACE)[0].get('url').split('userReviewId=')[1],
            'title': title,
            'content': content,
            'score': score(raw_review),
            'created_at': created_at(review_info),
            'version': version(review_info),
            'reviewer_id': raw_review.xpath('./ns:HBoxView', namespaces=NAMESPACE)[1].xpath('./ns:TextView[@topInset="0"]/ns:SetFontStyle/ns:GotoURL', namespaces=NAMESPACE)[0].get('url').split('userProfileId=')[1],
            'lang': find_out_language(REGIONS[region]['langs'], content, title),
            'region': region
        })
    return reviews


def version(review_meta):
    return review_meta[1].replace('Version', '').strip()


def created_at(review_meta):
    raw = review_meta[2].strip()
    try:
        return datetime.strptime(raw, '%d %B %Y')
    except ValueError:
        return datetime.strptime(raw, '%b %d, %Y')


def score(raw_review):
    raw_score = raw_review.xpath('./ns:HBoxView[@bottomInset="3"]/ns:HBoxView[@stretchiness="1"]/ns:HBoxView',
                                 namespaces=NAMESPACE)[0].get('alt').replace('stars', '').replace('star', '').strip()
    return int(raw_score) * 20
