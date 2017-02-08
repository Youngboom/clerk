import json
import urllib.request
import urllib.parse

from guess_language import guess_language
from langdetect import detect_langs
from langdetect.lang_detect_exception import LangDetectException
from translate import Translator

import settings

UNKNOWN_LANGUAGE = 'UNKNOWN'


def find_out_language(candidate_languages, *args):
    candidates = []
    for sample in args:
        candidate = guess_language(sample)
        if candidate != UNKNOWN_LANGUAGE and candidate in candidate_languages:
            candidates.append(candidate)
        try:
            for candidate in detect_langs(sample):
                if candidate.lang in candidate_languages:
                    candidates.append(candidate.lang)
        except LangDetectException:
            continue

    if len(candidates) == 0:
        return None
    leading_candidate = {
        'lang': candidates[0],
        'count': candidates.count(candidates[0])
    }
    for leading_candidate in candidates[1:0]:
        if leading_candidate['count'] < candidates.count(candidate):
            leading_candidate['lang'] = candidate
            leading_candidate['size'] = candidates.count(candidate)
    if leading_candidate['lang'] == UNKNOWN_LANGUAGE:
        return None
    return leading_candidate['lang']


def translate(statement, from_lang="en", to_lang="en"):
    from_lang = from_lang.lower().replace('_', '-')
    to_lang = to_lang.lower().replace('_', '-')

    if to_lang == "ko" and from_lang in ["en", "ja", "zh-tw", "zh-cn", "zh"]:
        return translate_by_naver(statement, from_lang)
    try:
        return Translator(from_lang=from_lang, to_lang=to_lang).translate(statement)
    except:
        return statement


def translate_by_translator(statement, from_lang="en", to_lang="en"):
    from_lang = from_lang.lower().replace('_', '-')
    to_lang = to_lang.lower().replace('_', '-')
    return Translator(from_lang=from_lang, to_lang=to_lang).translate(statement)


def translate_by_naver(statement, from_lang="en"):
    if from_lang == "zh":
        from_lang = "zh-TW"
    from_lang = from_lang.replace("tw", "TW")
    from_lang = from_lang.replace("cn", "CN")
    to_lang = "ko"

    allowed_langs = ["ko", "en", "ja", "zh-TW", "zh-CN"]
    assert from_lang in allowed_langs

    data = "source={}&target={}&text={}".format(from_lang, to_lang, urllib.parse.quote(statement))
    url = "https://openapi.naver.com/v1/language/translate"
    request = urllib.request.Request(url)
    request.add_header("X-Naver-Client-Id", settings.NAVER["CLIENT_ID"])
    request.add_header("X-Naver-Client-Secret", settings.NAVER["CLIENT_SECRET"])
    response = urllib.request.urlopen(request, data=data.encode("utf-8"))
    rescode = response.getcode()
    if (rescode == 200):
        resp = response.read().decode('utf-8')
        return json.loads(resp)["message"]["result"]["translatedText"]
    else:
        return Translator(from_lang=from_lang, to_lang=to_lang).translate(statement)
