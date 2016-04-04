import asyncio
import json

import aiohttp
from helper.lang import translate, UNKNOWN_LANGUAGE
import settings


class Slack(object):
    def __init__(self, store):
        self.latest_review_ids = []
        self.store = store

    @asyncio.coroutine
    def surveillance(self, reviews):
        for review in reviews:
            print(review)
            if review['id'] in self.latest_review_ids:
                return

            if len(review['content']) < 5:
                return

            self.latest_review_ids.append(review['id'])
            if len(self.latest_review_ids) > 30:
                del self.latest_review_ids[0]

            version = (" - {}".format(review['version'])) if not review.get('version', '').isspace() else ""

            yield from self.alert(review.get('name', 'Unknown'), {
                'title': self.refine_title(review, self.translate_to_english(review['lang'], review['title'])) + version,
                'text': self.translate_to_english(review['lang'], review['content'])
            })

    @asyncio.coroutine
    def alert(self, name, attachment):
        url = 'https://hooks.slack.com/services/{}'.format(settings.SLACK_TOKEN)
        payload = {
            'channel': settings.SLACK_CHANNEL[self.store],
            'username': "Reviewer : " + (name if not name.isspace() else "Anonymous"),
            'icon_emoji': settings.SLACK_EMOJI,
            "attachments": [attachment]
        }
        response = yield from aiohttp.request('POST', url, data={"payload": json.dumps(payload)})
        assert response.status == 200

    @staticmethod
    def star(score):
        star_mark = ''
        for i in range(1, 6):
            if i <= score / 20:
                star_mark = star_mark + '★'
            else:
                star_mark = star_mark + '☆'
        return star_mark

    @staticmethod
    def translate_to_english(lang, content):
        if content is None:
            return None

        except_languages = ['ko']

        if lang not in [UNKNOWN_LANGUAGE, 'en'] + except_languages:
            translated = translate(content, lang, to_lang='en')
            if 'MYMEMORY' not in translated:
                return '(TRANSLATE) {}\n(ORIGIN) {}'.format(translated, content)
        return content

    @staticmethod
    def refine_title(review, title):
        return '[{}-{}][{}]\n' \
        '{}'.format(review['region'], review['lang'], Slack.star(review['score']), title)