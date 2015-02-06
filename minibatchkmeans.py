import biggus
import h5py
from itertools import *
from sklearn.cluster import MiniBatchKMeans as kmeans

# https://github.com/bmcfee/ml_scraps/blob/master/BufferedEstimator.py
from BufferedEstimator import BufferedEstimator

wordvec = biggus.NumpyArrayAdapter(h5py.File('model/wordvec.hdf5')['wordvec'])

def grouper(iterable, n, fillvalue=None):
    "Collect data into fixed-length chunks or blocks"
    args = [iter(iterable)] * n
    return izip_longest(fillvalue=fillvalue, *args)

clusters = kmeans(n_clusters=500, max_iter=10, random_state=0)

def generator(X):
    for i, x in enumerate(X):
        if i % 10000 == 0:
            logging.info('Throwing seq #{0}'.format(i))
        yield x.ndarray()

buf_est = BufferedEstimator(clusters, batch_size=1000)
buf_est.fit(generator(wordvec))
