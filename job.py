import asyncio
import random
from action.slack import Slack
import settings
from speaker.play import REGIONS as PLAY_REGIONS, GOOGLE_PLAY
from speaker.play import review as play_review
from speaker.appstore import REGIONS as APPSTORE_REGIONS, APPSTORE
from speaker.appstore import review as appstore_review


def tasks():
    for region in PLAY_REGIONS.keys():
        yield task(GOOGLE_PLAY, play_review.latest_reviews, settings.PLAY_APP_CODE, region)
    for region in APPSTORE_REGIONS.keys():
        yield task(APPSTORE, appstore_review.latest_reviews, settings.APPSTORE_CODE, region)


@asyncio.coroutine
def task(store, latest_reviews, code, region, buffer=5):
    slack = Slack(store)
    while True:
        reviews = yield from latest_reviews(code, region, buffer)
        yield from slack.surveillance(reviews)
        yield from asyncio.sleep(settings.SHIFT_SEC + random.randrange(0, 100))


loop = asyncio.get_event_loop()
loop.run_until_complete(asyncio.wait([task for task in tasks()]))
loop.close()
