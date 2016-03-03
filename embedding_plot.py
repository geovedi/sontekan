from matplotlib import pylab
from sklearn.decomposition import PCA

def plot(words):
    %matplotlib inline
    embeddings = [model[w] for w in words]

    pca = PCA(n_components=2)  
    two_d_embeddings = pca.fit_transform(embeddings)

    pylab.figure(figsize=(5,5))  # in inches
    for i, label in enumerate(words):
        x, y = two_d_embeddings[i,:]
        pylab.scatter(x, y)
        pylab.annotate(label, xy=(x, y), xytext=(5, 2), textcoords='offset points', ha='right', va='bottom')
    pylab.show()

plot("pizza hamburger steak car motorcycle lamb cat cow sushi horse pork pig".split())
