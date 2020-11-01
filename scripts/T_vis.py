import os,sys
import numpy as np
from glob import glob
sys.path.append('../')
from T_util import writeh5


opt = sys.argv[1]

DYT='/n/pfister_lab2/Lab/vcg_natural/YouTube-VIS/'
if opt[0] == '0':
    if opt == '0': # youtube-vos example
        # sa2 idm
        from scipy.misc import imread
        sn = '25c750c6db'
        fn = DYT + 'train/Annotations/%s/' % sn
        ims = sorted(glob(fn + '*.png'))
        im = imread(ims[0])
        out = np.zeros([len(ims),im.shape[0],im.shape[1]],np.uint8)
        for i in range(len(ims)):
            out[i] = imread(ims[i])[:,:,0]
        writeh5('db/vis/seg_%s.h5' % sn, out)

    elif opt == '0.1': # youtube-vos example
        # sa vis
        from imageio import imread
        from vidtool import videoUtil as vutil
        sn = '1471274fa7'
        fn = DYT + 'train/JPEGImages/%s/' % sn
        ims = sorted(glob(fn + '*.jpg'))
        fn = DYT + 'train/Annotations/%s/' % sn
        segs = sorted(glob(fn + '*.png'))
        im = imread(ims[0])
        out = np.zeros([len(ims)] + list(im.shape),np.uint8)
        for i in range(len(ims)):
            out[i] = vutil.visSeg(imread(ims[i]), imread(segs[i])[:,:,0])
        vutil.writegif('db/vis/gif_%s.gif' % sn, out)
