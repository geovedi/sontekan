# -*- coding: utf-8 -*-

import logging
logging.basicConfig(
    format='%(asctime)s [%(process)d] [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    level=logging.INFO)

import plac
import codecs
import regex as re


class Token(object):
    def __init__(self, index=0, word=None, tag='_', head=0, label='_'):
        self.index = index
        self.word = word
        self.tag = tag
        self.head = int(head)
        self.label = label

    def __repr__(self):
        return (
            'Token(index={0}, word={1}, tag={2}, head={3}, label={4})'
            .format(self.index, self.word, self.tag, self.head, self.label))


BOS = Token(word='<s>', head=-1)
EOS = Token(word='</s>', head=0)
punct_pat = re.compile(r'\p{P}+')


def main(corpus_input, target):
    def write_wc(word, context):
        try:
            with codecs.open('{0}.pairs'.format(target), 'a', 'utf-8') as out:
                out.write(u'{0} {1}\n'.format(word, context))
        except Exception, e:
            logging.error(e)

    def process(tokens):
        contexts = []
        for token in tokens[1:-1]:

            if tokens[token.head].label in ['adpmod']:
                head = tokens[token.head].head
                label = ':'.join([tokens[token.head].label,
                                  tokens[token.head].word])
            else:
                head = token.head
                label = token.label

            if not punct_pat.sub('', token.word) or not punct_pat.sub(
                '', tokens[token.head].word):
                continue

            if tokens[token.head].word in ['<s>', '</s>']:
                continue

            # forward: scientist - australian/amod, discovers/nsubj-1
            word = tokens[head].word
            context = '_'.join([label, token.word])
            write_wc(word, context)

            # reverse: australian - scientist/amod-1
            word = token.word
            context = '_'.join([label + ':I', tokens[head].word])
            write_wc(word, context)

    sentence = [BOS]
    sentence_no = 0

    for line in codecs.open(corpus_input, 'r', 'utf-8'):
        parts = line.strip().lower().split()
        if parts:
            sentence.append(Token(index=parts[0],
                                  word=parts[1],
                                  tag=parts[3],
                                  head=parts[6],
                                  label=parts[7]))
        else:
            sentence.append(EOS)
            process(sentence)
            sentence = [BOS]
            sentence_no += 1

            if sentence_no % 10000 == 0:
                logging.info(('sentence', sentence_no))

if __name__ == '__main__':
    plac.call(main)
