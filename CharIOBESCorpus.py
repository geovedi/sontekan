# O is not needed

class CharIOBESCorpus(object):
    def __init__(self, fname):
        self.fname = fname

    def iob(self, seq):                                                       
        if len(seq) == 1: return ['{0}/S'.format(seq[0])]
        lab = ['I'] * len(seq)
        lab[0] = 'B'
        lab[-1] = 'E'
        return map('|'.join, zip(seq, lab))

    def __iter__(self):
        with io.open(self.fname, 'r', encoding='utf-8') as fin:
            for sentence in fin:
                yield map(self.iob, sentence.split())[0]
