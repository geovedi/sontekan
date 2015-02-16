import h5py
import cPickle as pickle
import numpy as np
import scipy.sparse as sp

# XXX: Store and load CSR from HDF5?

## Corpus: Save
f = h5py.File('corpus.h5')
for par in ('data', 'row', 'col', 'shape'):
    f.create_dataset(par, data=np.array(getattr(corpus.matrix, par)))
corpus.__dict__.pop('matrix')
pickle.dump(corpus, open('corpus.p', 'wb'), protocol=2)

## Corpus: Load
corpus = pickle.load(open('corpus.p'))
f = h5py.File('corpus.h5')
corpus.matrix = sp.coo_matrix((f['data'], (f['row'], f['col'])),
                              shape=f['shape'], dtype=np.float64)


## Model: Save
f = h5py.File('corpus.h5')
for field in ['word_vectors', 'word_biases', 'vectors_sum_gradients', 'biases_sum_gradients']:
    f.create_dataset(field, data=model.__dict__[field])
    model.__dict__.pop(field)
pickle.dump(model, open('corpus.p', 'wb'), protocol=2)

## Model: Load
model = pickle.load(open('model.p'))
f = h5py.File('corpus.h5')
for field in ['word_vectors', 'word_biases', 'vectors_sum_gradients', 'biases_sum_gradients']:
    model.__dict__[field] = f[field]
