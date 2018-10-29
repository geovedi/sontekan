#!/usr/bin/env python3

import os
import re
import argparse
import unicodedata

from html.entities import name2codepoint
from pathlib import Path, PurePath
from text_unidecode import unidecode

CHAR_ENTITY_PATTERN = re.compile('&(%s);' % '|'.join(name2codepoint))
DECIMAL_PATTERN = re.compile('&#(\d+);')
HEX_PATTERN = re.compile('&#x([\da-fA-F]+);')
QUOTE_PATTERN = re.compile(r'[\']+')
ALLOWED_CHARS_PATTERN = re.compile(r'[^-a-z0-9]+')
DUPLICATE_DASH_PATTERN = re.compile('-{2,}')
DEFAULT_SEPARATOR = '-'


def slugify_text(text):
    if not isinstance(text, str):
        text = str(text, 'utf-8', 'ignore')

    text = QUOTE_PATTERN.sub(DEFAULT_SEPARATOR, text)
    text = unidecode(text)
    text = CHAR_ENTITY_PATTERN.sub(
        lambda m: unichr(name2codepoint[m.group(1)]), text)

    try:
        text = DECIMAL_PATTERN.sub(lambda m: unichr(int(m.group(1))), text)
    except Exception:
        pass

    try:
        text = HEX_PATTERN.sub(lambda m: unichr(int(m.group(1), 16)), text)
    except Exception:
        pass

    text = unicodedata.normalize('NFKD', text)
    text = text.lower()
    text = QUOTE_PATTERN.sub('', text)
    text = re.sub(ALLOWED_CHARS_PATTERN, DEFAULT_SEPARATOR, text)
    text = DUPLICATE_DASH_PATTERN.sub(DEFAULT_SEPARATOR,
                                      text).strip(DEFAULT_SEPARATOR)
    return text


def slugify_fpath(fpath):
    target_stem = slugify_text(fpath.stem.split('.')[0])
    suffixes = map(lambda x: slugify_text(x.lower()[1:]), fpath.suffixes)
    target_fname = '.'.join([target_stem] + list(filter(None, suffixes)))
    return fpath.with_name(target_fname)


def main():
    parser = argparse.ArgumentParser(description='File renamer')
    parser.add_argument(
        'file', metavar='FILE', type=str, nargs='+', help='Filename(s)')

    args = parser.parse_args()

    for source in set(args.file):
        source = source.rstrip('.')
        source_path = PurePath(source)
        target_path = slugify_fpath(source_path)


        if source_path != target_path:
            try:
                Path(source_path).rename(Path(target_path))
                print("Renamed '{0}' to '{1}'".format(source_path, target_path))
            except Exception as e:
                print(e)
                pass


if __name__ == '__main__':
    main()
