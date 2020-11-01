# sbatch ~/ss/do_job.sh
import h5py
import os,sys
sys.path.append('../')
from T_util import ngLayer,readh5,vast2Seg,get_union,get_unionA,readtxt,arrToStr
from imageio import imread,volread
import numpy as np

opt=sys.argv[1]


if opt[0]  == '0':
    # cshL 9092
    # csgL 9092 06
    # sa ng
    import neuroglancer
    ip='localhost' # or public IP of the machine for sharable display
    port=9092 # change to an unused port number
    neuroglancer.set_server_bind_address(bind_address=ip,bind_port=port)
    viewer=neuroglancer.Viewer()
    
    res = [5,5,250]
    if opt =='0': # load train
        seg = readh5('db/vis/seg_25c750c6db.h5')
        with viewer.txn() as s:
            s.layers.append(name='seg',layer=ngLayer(seg,res))

    print(viewer)
