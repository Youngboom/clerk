import re

re_pattern = re.compile(u'[^\u0000-\uD7FF\uE000-\uFFFF]', re.UNICODE)


def remove_emoji(origin):
    return re_pattern.sub(u'\uFFFD', origin)
