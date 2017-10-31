'''
MoCap6.py

Dataset generated by motion capture of humans performing various exercises
True labels of the exercises in Data.TrueParams['Z'] run from 0 through 11
'''

import numpy as np
import readline
import os
import scipy.io

from bnpy.data import GroupXData

datasetdir = os.path.sep.join(
    os.path.abspath(__file__).split(os.path.sep)[:-1])

if not os.path.isdir(datasetdir):
    raise ValueError('CANNOT FIND MOCAP6 DATASET DIRECTORY:\n' + datasetdir)

matfilepath = os.path.join(datasetdir, 'rawData', 'MoCap6.mat')
if not os.path.isfile(matfilepath):
    raise ValueError('CANNOT FIND MOCAP6 DATASET MAT FILE:\n' + matfilepath)


def get_data(**kwargs):
    Data = GroupXData.read_from_mat(matfilepath)
    Data.summary = get_data_info()
    Data.name = get_short_name()
    # Verify that true state space is indexed starting at 0, not 1
    # Violating this can cause bugs in the alignment code
    assert Data.TrueParams['Z'].min() == 0
    assert Data.TrueParams['Z'].max() == 11
    return Data


def get_data_info():
    return 'Six MoCap sequences from mocap.cs.cmu.edu'


def get_short_name():
    return 'MoCap6'


# How to make MAT file
###########################################################
# Exact commands to execute in python interpreter (by hand)
# to create a MAT file from the raw data distributed by NPBayesHMM toolbox
# ---------
# >> dpath = '/path/to/git/NPBayesHMM/data/mocap6/'
# >> SaveVars = loadFromPlainTextFiles(dpath)
# >> scipy.io.savemat('/path/to/git/bnpy-dev/datasets/MoCap6.mat', SaveVars)

# Reproducibility Notes
# ---------
# Mimics the following files in NPBayesHMM repository
# * readSeqDataFromPlainText.m
# * ARSeqData.m (specifically 'addData' method)

def savePlainTextFilesToMATFile(dpath, outmatfile):
    SaveVars = loadFromPlainTextFiles(dpath)
    scipy.io.savemat(outmatfile, SaveVars, oned_as='row')


def loadFromPlainTextFiles(dpath):
    '''
    Returns
    --------
    DataDict : dict with fields
    * X : data matrix
    * Xprev : matrix of previous observations
    * seqNames : list of strings, one per sequence
    * doc_range : ptr to where each seq stops and starts
    * TrueZ : 1d array of true labels, concatenated for all sequences.
        Labels run from 0, 1, ... 11
    '''
    with open(os.path.join(dpath, 'SeqNames.txt'), 'r') as f:
        seqNameList = [line.strip() for line in f.readlines()]

    with open(os.path.join(dpath, 'zTrue.dat'), 'r') as f:
        zTrueList = [line.strip() for line in f.readlines()]

    allXList = list()
    allXprevList = list()
    keepZList = list()
    doc_range = [0]
    for ii, seqName in enumerate(seqNameList):
        curZ = np.asarray(zTrueList[ii].split(), dtype=np.int32)
        seqfpath = os.path.join(dpath, seqName + '.dat')
        curX = np.loadtxt(seqfpath)
        curT = curZ.size
        allXList.append(curX[1:])
        allXprevList.append(curX[:-1])
        keepZList.append(curZ[1:])
        doc_range = np.hstack([doc_range, doc_range[-1] + curT - 1])

    X = np.vstack(allXList)
    Xprev = np.vstack(allXprevList)
    Z = np.hstack(keepZList)

    for seqID in range(doc_range.size - 1):
        start = doc_range[seqID]
        stop = doc_range[seqID + 1]
        assert np.allclose(X[start:stop - 1], Xprev[start + 1:stop])

    # Make this a zero-indexed state space
    Z = np.asarray(Z - 1, dtype=np.int32)
    return dict(X=X, Xprev=Xprev, TrueZ=Z, seqNames=seqNameList,
                doc_range=np.asarray(doc_range, dtype=np.int32),
                )
