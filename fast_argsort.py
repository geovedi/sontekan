import numpy

try:
    import bottleneck
    def argsort(x, topn=None):
        if topn is None:
            topn = x.size
        if topn <= 0:
            return []
        if topn >= x.size:
            return numpy.argsort(x)[::-1]
        biggest = bottleneck.argpartsort(x, x.size - topn)[-topn:]
        return biggest.take(numpy.argsort(x.take(biggest))[::-1])
except ImportError:
    def argsort(x, topn=None):
        if topn is None:
            topn = x.size
        return numpy.argsort(x)[::-1][:topn]
