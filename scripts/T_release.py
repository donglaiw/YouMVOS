import os,sys,shutil
import json
import numpy as np
sys.path.append('../')
from T_util import U_mkdir
from imageio import imread,imwrite

opt = sys.argv[1]
job_id=0;job_num=1;
if len(sys.argv)>3:
    job_id = int(sys.argv[2])
    job_num = int(sys.argv[3])

Dv='/n/pfister_lab2/Lab/vcg_natural/YouTop200/'
Ds='/n/pfister_lab2/Lab/donglai/YouTop200/db/share/{}/seg_prop_out/seg_%05d.png'

if opt[0] == '0':
    videos = json.load(open('data/video.json'))
    video_names = videos.keys()

    if opt == '0': # get jpg images
        Do = Dv + 'release/JPEGImages/'
        video_names=['cooking/3nUKwvFsjA4']
        for video_name in video_names:
            fps = int(np.round(videos[video_name]['fps']))
            num_im = videos[video_name]['num_frame']
            if fps in [25,30]:
                step = 5
            elif fps in [24]:
                step = 4
            elif fps in [27]:
                step = 3
            Do2 = Do + video_name.replace('/','_')
            U_mkdir(Do2, 2)
            for i in range(0, num_im, step)[job_id::job_num]:
                sn = Do2 + '/%05d.jpg' % (1+i)
                if not os.path.exists(sn):
                    shutil.movefile(Do2 + '/image_%05d.jpg' % (1+i), sn)
                """
                if not os.path.exists(sn):
                    im = imread(Dv + video_name + '/frame/image_%05d.png' % (1+i))
                    imwrite(sn, im)
                """
    elif opt == '0.1': # copy annotation
        Do = Dv + 'release/Annotations/'
        video_names=['cooking/3nUKwvFsjA4']
        for video_name in video_names:
            fps = int(np.round(videos[video_name]['fps']))
            num_im = videos[video_name]['num_frame']
            im_size = videos[video_name]['size']
            black = np.zeros(im_size, np.uint8)
            if fps in [25,30]:
                step = 5
            elif fps in [24]:
                step = 4
            elif fps in [27]:
                step = 3
            Do2 = Do + video_name.replace('/','_')
            U_mkdir(Do2)
            Ds2 = Ds.format(video_name)
            for i in range(0, num_im, step)[job_id::job_num]:
                sn = Do2 + '/%05d.png' % (1+i)
                if not os.path.exists(sn):
                    sn2 = Ds2 % (i//step)
                    if os.path.exists(sn2):
                        shutil.copyfile(sn2, sn)
                    else:
                        imwrite(sn, black)
