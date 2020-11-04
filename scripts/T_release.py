import os,sys,shutil
import json
import numpy as np
sys.path.append('../')
from T_util import U_mkdir,writetxt,readtxt
from imageio import imread,imwrite

opt = sys.argv[1]
job_id=0;job_num=1;
if len(sys.argv)>3:
    job_id = int(sys.argv[2])
    job_num = int(sys.argv[3])

Dv = '/n/pfister_lab2/Lab/vcg_natural/YouTop200/'
Dvr = Dv + 'release/'
Ds='/n/pfister_lab2/Lab/donglai/YouTop200/db/share/{}/seg_prop_out/seg_%05d.png'

if opt[0] == '0':
    videos = json.load(open('data/video.json'))
    video_names = videos.keys()

    if opt == '0': # get jpg images
        Do = Dv + 'release/JPEGImages/'
        #video_names=['cooking/3nUKwvFsjA4']
        for video_name in video_names:
            print(video_name)
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
                sn2 = Do2 + '/image_%05d.jpg' % (1+i)
                if not os.path.exists(sn):
                    if os.path.exists(sn2):
                        shutil.move(sn2, sn)
                    else:
                        im = imread(Dv + video_name + '/frame/image_%05d.png' % (1+i))
                        imwrite(sn, im)
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
elif opt[0] == '1':
    videos = json.load(open('data/video.json'))
    video_names =list(videos.keys())
    #  train/val/test
    ratio = [15,2,3]
    if opt == '1':
        np.random.seed(1234)
        sc = np.random.random([20,10])
        train=[];val=[];test=[]
        for col in range(10):
            sid = np.argsort(sc[:,col])
            train += [video_names[col*20+sid[i]] for i in range(ratio[0])]
            val += [video_names[col*20+sid[i]] for i in range(ratio[0], ratio[0]+ratio[1])]
            test += [video_names[col*20+sid[i]] for i in range(ratio[0]+ratio[1], sum(ratio))]
        writetxt('data/yt_train.txt', train)
        writetxt('data/yt_val.txt', val)
        writetxt('data/yt_test.txt', test)
    elif opt == '1.1':
        from vidtool.videoUtil import getVideoFrameStep
        train = readtxt('data/yt_train.txt')
        kk = 'movie_trailer'
        kk = 'music_video'
        pp = 'https://lichtman.rc.fas.harvard.edu/vcg/youtop-vis/youtube/proofread/%s/test/'%kk
        ss = '_seg.html?fps=%d&pref=stm_out_&suf=_shot_out'
        for x in train :
            if kk in x:
                #print(x[:-1])
                print(pp + x[x.find('/')+1:-1] + '_shot_out.html')
                #print(pp + x[x.find('/')+1:-1] + ss % getVideoFrameStep(int(np.round(videos[x[:-1]]['fps']))))
elif opt[0] == '2':
    if opt == '2':
        fn = Dvr + 'info/video.json'
        videos = json.load(open(fn))
        kks = list(videos.keys())
        for kk in kks:
            videos[kk.replace('/','_')] = videos[kk]
            del videos[kk]
        json.dump(videos, open(fn,'w'))

