# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import regex as re
import fileinput
import ftfy

def main():
    for line in fileinput.input():
        line = ftfy.fix_text(line.decode('utf-8'))
        tokens = line.split()
        new_tokens = []
        for token in tokens:
            if re.search(r'^[\p{P}\p{S}]+$', token):
                token = '$'
            elif re.search(r'^\p{N}+$', token):
                token = '0'
            elif token == "can't":
                token = 'can\tnot'
            elif re.search(r"'(m|s|re|d|ll)", token):
                token = re.sub(r"(\w+)'(m|s|re|d|ll)$", r"\1\t'\2", token)
            elif re.search(r"(\w+)n't$", token):
                token = re.sub(r"(\w+)n't$", r"\1\tn't", token)
            new_tokens.append(token)
        line = '\t'.join(new_tokens)
        print line.encode('utf-8')

if __name__ == '__main__':
    main()
