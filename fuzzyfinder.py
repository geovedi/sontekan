# -*- coding: utf-8 -*-

from __future__ import unicode_literals


def fuzzyfinder(text, collection):
    suggestions = []
    pat = '.*?'.join(map(re.escape, text))
    regex = re.compile('%s' % pat)
    for item in sorted(collection):
        r = regex.search(item)
        if r:
            suggestions.append((len(r.group()), r.start(), item))
    return (z for _, _, z in sorted(suggestions))
