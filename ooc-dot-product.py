import h5py
import dask.array as da
from dask.array.into import *

f = h5py.File('vector.h5')
a = da.from_array(f['vector'], blockshape=(1000, 1000))
result = a.dot(a.T)

into('vector_dot_product.h5::/vector', result)
