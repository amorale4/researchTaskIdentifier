"""
=======================================
Clustering text documents using k-means
=======================================

This is an example showing how the scikit-learn can be used to cluster
documents by topics using a bag-of-words approach. This example uses
a scipy.sparse matrix to store the features instead of standard numpy arrays.

Two feature extraction methods can be used in this example:

  - TfidfVectorizer uses a in-memory vocabulary (a python dict) to map the most
    frequent words to features indices and hence compute a word occurrence
    frequency (sparse) matrix. The word frequencies are then reweighted using
    the Inverse Document Frequency (IDF) vector collected feature-wise over
    the corpus.

  - HashingVectorizer hashes word occurrences to a fixed dimensional space,
    possibly with collisions. The word count vectors are then normalized to
    each have l2-norm equal to one (projected to the euclidean unit-ball) which
    seems to be important for k-means to work in high dimensional space.

    HashingVectorizer does not provide IDF weighting as this is a stateless
    model (the fit method does nothing). When IDF weighting is needed it can
    be added by pipelining its output to a TfidfTransformer instance.

Two algorithms are demoed: ordinary k-means and its more scalable cousin
minibatch k-means.

It can be noted that k-means (and minibatch k-means) are very sensitive to
feature scaling and that in this case the IDF weighting helps improve the
quality of the clustering by quite a lot as measured against the "ground truth"
provided by the class label assignments of the 20 newsgroups dataset.

This improvement is not visible in the Silhouette Coefficient which is small
for both as this measure seem to suffer from the phenomenon called
"Concentration of Measure" or "Curse of Dimensionality" for high dimensional
datasets such as text data. Other measures such as V-measure and Adjusted Rand
Index are information theoretic based evaluation scores: as they are only based
on cluster assignments rather than distances, hence not affected by the curse
of dimensionality.

Note: as k-means is optimizing a non-convex objective function, it will likely
end up in a local optimum. Several runs with independent random init might be
necessary to get a good convergence.

"""

# Author: Peter Prettenhofer <peter.prettenhofer@gmail.com>
#         Lars Buitinck <L.J.Buitinck@uva.nl>
# License: BSD 3 clause

from __future__ import print_function

from sklearn.datasets import fetch_20newsgroups
from sklearn.decomposition import TruncatedSVD
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_extraction.text import HashingVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import Normalizer
from sklearn import metrics

from sklearn.cluster import KMeans, MiniBatchKMeans

import logging
from optparse import OptionParser
import sys
from time import time
import math
import numpy as np
import pickle

def chaufunc(x, mu, std, n):
    #z = n*(x - mu)/std
    var = std**2
    return (1/math.sqrt(2*math.pi*var)*math.e**(-((x-mu)**2)/var))*n

def main():
    print("Extracting features from the training dataset using a sparse vectorizer")
    #t0 = time()

    # Display progress logs on stdout
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s %(levelname)s %(message)s')

    # parse commandline arguments
    op = OptionParser()
    op.add_option("--lsa",
                  dest="n_components", type="int",
                  help="Preprocess documents with latent semantic analysis.")
    op.add_option("--no-minibatch",
                  action="store_false", dest="minibatch", default=True,
                  help="Use ordinary k-means algorithm (in batch mode).")
    op.add_option("--no-idf",
                  action="store_false", dest="use_idf", default=True,
                  help="Disable Inverse Document Frequency feature weighting.")
    op.add_option("--use-hashing",
                  action="store_true", default=False,
                  help="Use a hashing feature vectorizer")
    op.add_option("--n-features", type=int, default=10000,
                  help="Maximum number of features (dimensions)"
                       " to extract from text.")
    op.add_option("--verbose",
                  action="store_true", dest="verbose", default=False,
                  help="Print progress reports inside k-means algorithm.")

    print(__doc__)
    op.print_help()
    
    (opts, args) = op.parse_args([""])
    print (len(args))
    if len(args) > 1:
        op.error("this script takes no arguments.")
        sys.exit(1)
    
    #get the title and future work sections and pass that as the data
    dataFile = 'PickleCreation/AllDataPickle_e1.pk'
    data = pickle.load(open(dataFile,'rb'))
    print ("size of data: " + str(len(data)) )
    myData = []
    for key in data:
        future_work_section = data[key][9]
        title_section = data[key][0]
        if not (future_work_section == ""):
            myData.append(title_section + " " + future_work_section)

    numDocs = len(myData)
    print ("future-title docs = " + str(numDocs))    

    
    if opts.use_hashing:
        if opts.use_idf:
            # Perform an IDF normalization on the output of HashingVectorizer
            hasher = HashingVectorizer(n_features=opts.n_features,
                                       stop_words='english', non_negative=True,
                                       norm=None, binary=False)
            vectorizer = make_pipeline(hasher, TfidfTransformer())
        else:
            vectorizer = HashingVectorizer(n_features=opts.n_features,
                                           stop_words='english',
                                           non_negative=False, norm='l2',
                                           binary=False)
    else:
        vectorizer = TfidfVectorizer(max_df=0.5, max_features=opts.n_features,
                                     min_df=2, stop_words='english',
                                     use_idf=opts.use_idf)
    
    X = vectorizer.fit_transform(myData)
    
    if opts.n_components:
        print("Performing dimensionality reduction using LSA")
        t0 = time()
        # Vectorizer results are normalized, which makes KMeans behave as
        # spherical k-means for better results. Since LSA/SVD results are
        # not normalized, we have to redo the normalization.
        svd = TruncatedSVD(opts.n_components)
        lsa = make_pipeline(svd, Normalizer(copy=False))

        X = lsa.fit_transform(X)

        print("done in %fs" % (time() - t0))

        explained_variance = svd.explained_variance_ratio_.sum()
        print("Explained variance of the SVD step: {}%".format(
            int(explained_variance * 100)))

        print()
        
    ###############################################################################
    # Do the actual clustering
    opts.minibatch = False
    true_k = 6
    if opts.minibatch:
        #km = MiniBatchKMeans(n_clusters=true_k, init='k-means++', n_init=1,
        #                     init_size=1000, batch_size=1000, verbose=opts.verbose)
        km = MiniBatchKMeans(n_clusters=true_k, init='k-means++', n_init=1,
                             init_size=1000, batch_size=1000, verbose=opts.verbose)
    else:
        km = KMeans(n_clusters=true_k, init='k-means++', max_iter=100, n_init=1,
                    verbose=opts.verbose)

    
    #Clustering the title-futurework pairs
    km.fit(X)
    print (len(km.cluster_centers_))
    print (X.size)
    
    # contains a dictionary of lists where the keys are the cluster centers
    norm_squared_dic = {}
    for i in range(numDocs):
        key = km.labels_[i]
        if key in norm_squared_dic:
            norm_squared_dic[key].append((i, -km.score(X[i,:])))
        else:
            norm_squared_dic[key] = [(i, -km.score(X[i,:]))]

        #min max mean
    outliers = []
    for key in norm_squared_dic:
        dist_list = [ item for (doc_key, item) in norm_squared_dic[key] ]
        mu = np.mean(dist_list)
        std = np.std(dist_list)
        n = len(dist_list)
        for (doc_key,x) in norm_squared_dic[key]:
            chau_score = chaufunc(x, mu, std,n )
            if ( chau_score < 0.5 ):
                outliers.append((doc_key, x))
        #print (key, min(dist_list), max(dist_list), np.mean(dist_list), np.var(dist_list))
        
    #print (outliers)
    outliers_sorted = sorted(outliers,key=lambda k_v: k_v[1],reverse=True)
    print (outliers_sorted)   
        
if __name__ == "__main__":
    main()