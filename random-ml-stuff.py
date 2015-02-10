
def similarity_query(vec, topn=10):
    dst = np.dot(X, vec) / np.linalg.norm(X, axis=1) / np.linalg.norm(vec)
    word_ids = argsort(dst)
    return [(vocab[x], dst[x]) for x in word_ids[:topn] if x in vocab]

