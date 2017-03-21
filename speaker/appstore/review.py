import asyncio
import json
from helper.filter import remove_emoji
from helper.lang import find_out_language
from lxml import etree
from datetime import datetime
from helper.http_client import request
from speaker.appstore import NAMESPACE, REGIONS


@asyncio.coroutine
def latest_reviews(code, region, buffer_size):
    url = "https://itunes.apple.com/{}/rss/customerreviews/id={}/sortBy=mostRecent/json".format(region, code)
    body = yield from request(url)
    reviews = list()
    feed = json.loads(body.decode('utf-8')).get('feed')
    if feed is None:
        return reviews
    entries = feed.get('entry')
    if entries is None:
        return reviews
    for entry in entries:
        try:
            if entry.get('author') is None:
                continue
            title = entry['title']['label']
            content = entry['content']['label']
            reviews.append({
                'id': entry['id']['label'],
                'title': title,
                'content': content,
                'name': entry['author']['name']['label'],
                'score': score(entry['im:rating']['label']),
                'version': entry['im:version']['label'],
                'lang': find_out_language(REGIONS[region]['langs'], content, title),
                'region': region
            })
        except IndexError:
            pass
    return reviews


def score(rating):
    return int(rating) * 20
