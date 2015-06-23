# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import regex as re

def fuzzyfinder(text, collection):
    suggestions = []
    pat = re.compile('.*?'.join(map(re.escape, text)))
    for item in sorted(collection):
        r = pat.search(item)
        if r:
            suggestions.append((len(r.group()), r.start(), item))
    return [z for _, _, z in sorted(suggestions)]
