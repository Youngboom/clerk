import asyncio

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
            review['title'] = self.translate_to_english(review['lang'], review['title'])
            review['content'] = self.translate_to_english(review['lang'], review['content'])

            message = '*[{}-{}][{}]*\n' \
                      '*{}*\n' \
                      '{}\n'.format(review['region'], review['lang'], self.star(review['score']), review['title'], review['content'])

            if len(self.latest_review_ids) > 30:
                del self.latest_review_ids[0]

            yield from self.alert(message)

    @asyncio.coroutine
    def alert(self, message):
        channel = settings.SLACK_CHANNEL[self.store]
        url = 'https://vcnc.slack.com/services/hooks/slackbot?token={}&channel=%23{}'.format(settings.SLACK_TOKEN, channel)
        response = yield from aiohttp.request('POST', url, data=message)
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
                return '(TRANSLATE) ' + translated
        return content
