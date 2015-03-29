from sklearn.cluster import KMeans
import numpy as np
means=KMeans(n_clusters=8, init='k-means++', n_init=10, max_iter=300, tol=0.0001, precompute_distances=True, verbose=0, random_state=None, copy_x=True, n_jobs=1)
dataSet=np.random.rand(32,3)
print dataSet
out=means.fit(dataSet)
print out