import h5py
import cPickle as pickle
import numpy as np
import scipy.sparse as sp

# Corpus
# XXX: Store and load CSR from HDF5?

## Save
f = h5py.File('corpus.h5')
for par in ('data', 'row', 'col', 'shape'):
    f.create_dataset(par, data=np.array(getattr(corpus.matrix, par)))

corpus.__dict__.pop('matrix')
pickle.dump(corpus, open('corpus.p', 'wb'), protocol=2)

## Load
corpus = pickle.load(open('corpus.p'))
f = h5py.File('corpus.h5')
corpus.matrix = sp.coo_matrix((f['data'], (f['row'], f['col'])),
                              shape=f['shape'], dtype=np.float64)
