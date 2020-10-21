import os,sys
import json
import numpy as np
sys.path.append('../')
from T_util import U_mkdir
from imageio import imread,imwrite

opt = sys.argv[1]

Dv='/n/pfister_lab2/Lab/vcg_natural/YouTop200/'

if opt[0] == '0':
    videos = json.load(open('data/video.json'))
    video_names = videos.keys()

    if opt == '0': # get jpg images
        Do = Dv + 'release/'
        for video_name in video_names:
            fps = int(np.round(videos[video_name]['fps']))
            num_im = videos[video_name]['num_frame']
            if fps in [25,30]:
                step = 5
            elif fps in [24]:
                step = 4
            elif fps in [27]:
                step = 9
            Do2 = Do + video_name + 'image/'
            U_mkdir(Do2)
            for i in range(0, step, num_im):
