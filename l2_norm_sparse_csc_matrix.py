
import numpy as np
from scipy.sparse.sparsetools csr_scale_rows

def l2_norm(sparse_csc_matrix):
    # convert csc_matrix to csr_matrix which is done in linear time
    norm = sparse_csc_matrix.tocsr(copy=True)

    # compute the inverse of l2 norm of non-zero elements
    norm.data **= 2
    norm = norm.sum(axis=1)
    n_nzeros = np.where(norm > 0)
    norm[n_nzeros] = 1.0 / np.sqrt(norm[n_nzeros])
    norm = np.array(norm).T[0]

    # modify sparse_csc_matrix in place
    csr_scale_rows(sparse_csc_matrix.shape[0], sparse_csc_matrix.shape[1],
                   sparse_csc_matrix.indptr, sparse_csc_matrix.indices,
                   sparse_csc_matrix.data, norm)
