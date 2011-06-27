"""
An example of parser grammar with pyparsing library.
Read a number given in Indonesian words and return the numeric value

-- Copyright (C) 2011 Jim Geovedi <jim@geovedi.com>
   WTFPL (Do What The Fuck You Want To Public License) 
"""
from pyparsing import *
from operator import mul

def makeLiteral(str, val):
    ret = CaselessLiteral(str).setName(str)
    return ret.setParseAction(replaceWith(val))

BilanganKecil = [
    ("nol", 0),
    ("kosong", 0),
    ("satu", 1),
    ("dua", 2),
    ("tiga", 3),
    ("empat", 4),
    ("lima", 5),
    ("enam", 6),
    ("tujuh", 7),
    ("delapan", 8),
    ("sembilan", 9),
    ("sepuluh", 10),
    ("sebelas", 11),
    ("dua belas", 12),
    ("tiga belas", 13),
    ("empat belas", 14),
    ("lima belas", 15),
    ("enam belas", 16),
    ("tujuh belas", 17),
    ("delapan belas", 18),
    ("sembilan belas", 19),
    # dirty hack: these are not small numbers!
    ("seratus", 100),
    ("seribu", int(1e3)),
    ("sejuta", int(1e6)),
    ("semilyar", int(1e9)),
    ("setrilyun", int(1e12)),
]
kecil = Or([makeLiteral(str, val) for str, val in BilanganKecil])

BilanganPuluhan = [
    ("sepuluh", 10),
    ("dua puluh", 20),
    ("tiga puluh", 30),
    ("empat puluh", 40),
    ("lima puluh", 50),
    ("enam puluh", 60),
    ("tujuh puluh", 70),
    ("delapan puluh", 80),
    ("sembilan puluh", 90),
]
puluhan = Or([makeLiteral(str, val) for str, val in BilanganPuluhan])

BilanganRatusan = [
    ("seratus", 100),
    ("dua ratus", 200),
    ("tiga ratus", 300),
    ("empat ratus", 400),
    ("lima ratus", 500),
    ("enam ratus", 600),
    ("tujuh ratus", 700),
    ("delapan ratus", 800),
    ("sembilan ratus", 900),
]
ratusan = Or([makeLiteral(str, val) for str, val in BilanganRatusan])

BilanganRibuan = [
    ("seribu", 1000),
    ("dua ribu", 2000),
    ("tiga ribu", 3000),
    ("empat ribu", 4000),
    ("lima ribu", 5000),
    ("enam ribu", 6000),
    ("tujuh ribu", 7000),
    ("delapan ribu", 8000),
    ("sembilan ribu", 9000),
    ("sepuluh ribu", 10000),
    ("seratus ribu", 100000),
    ("dua ratus ribu", 200000),
    ("tiga ratus ribu", 300000),
    ("empat ratus ribu", 400000),
    ("lima ratus ribu", 500000),
    ("enam ratus ribu", 600000),
    ("tujuh ratus ribu", 700000),
    ("delapan ratus ribu", 800000),
    ("sembilan ratus ribu", 900000),
]
ribuan = Or([makeLiteral(str, val) for str, val in BilanganRibuan])

BilanganBesar = [
    ("ribu", int(1e3)),
    ("juta", int(1e6)),
    ("milyar", int(1e9)),
    ("trilyun", int(1e12)),
]
besar = Or([makeLiteral(str, val) for str, val in BilanganBesar])

wordprod = lambda t: reduce(mul, t)
wordsum = lambda t: sum(t)
numPart = (((((((kecil + 
                 Optional(ribuan)).setParseAction(wordsum) ^ ribuan) + 
                 Optional(ratusan)).setParseAction(wordsum) ^ ratusan) + 
                 Optional(puluhan)).setParseAction(wordsum) ^ puluhan) + 
                 Optional(kecil)).setParseAction(wordsum)
numWords = OneOrMore((numPart + 
                      Optional(besar)).setParseAction(wordprod)) \
                                      .setParseAction(wordsum) + StringEnd()

def test(str, expected):
    try:
        val = numWords.parseString(str)[0]
    except ParseException, pe:
        print "Parsing failed:"
        print str
        print "%s^--" % (' '*(pe.col-1)),
        print pe.msg
    else:
        print "'%s' -> %d" % (str, val),
        if val == expected:
            print "CORRECT"
        else:
            print "*** WRONG ***, expected %d" % expected

test("sepuluh", 10)
test("delapan ratus tujuh puluh lima", 875)
test("sepuluh ribu", 10000)
test("seribu satu", 1001)
test("seribu lima puluh", 1050)
test("seribu delapan ratus", 1800)
test("satu ribu dua puluh", 1020) # it's not common, but WTF
test("seribu delapan ratus tujuh puluh", 1870)
test("seribu delapan ratus tujuh puluh lima", 1875)
test("sejuta", 1000000)
test("sejuta lima ratus", 1000500)
test("sejuta lima ratus ribu", 1500000)
test("sejuta lima ratus ribu dua puluh satu", 1500021)
test("satu juta lima ratus ribu dua puluh satu", 1500021)
test("satu juta lima ratus ribu tiga ratus dua belas", 1500312)
test("tiga ratus juta", 300000000)
test("tiga ratus dua puluh lima juta", 325000000)
test("tiga ratus dua puluh lima juta enam ratus ribu", 325600000)
test("tiga ratus dua puluh lima juta enam ratus tiga puluh", 325000630)
test("tiga ratus dua puluh lima juta enam ratus tiga puluh tujuh", 325000637)
test("tiga ratus dua puluh lima juta enam ratus tiga puluh tujuh ribu", 325637000)
test("enam milyar", 600000000) # wrong
test("enam milyar", 6000000000)
test("sembilan milyar enam puluh delapan", 9000000068)
test("sembilan milyar enam puluh delapan ribu", 9000068000)
test("sepuluh milyarr", 10000000000) # typo
test("sepuluh milyar", 10000000000)
