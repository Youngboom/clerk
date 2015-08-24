from guess_language import guess_language
from langdetect import detect_langs
from langdetect.lang_detect_exception import LangDetectException
from translate import Translator

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
    return Translator(from_lang=from_lang, to_lang=to_lang).translate(statement)