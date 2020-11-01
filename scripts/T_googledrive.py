import os,sys
from glob import glob
import shutil
import numpy as np
import json

# pdb.set_trace = lambda: None

def U_mkdir(fn):
    if not os.path.exists(fn):
        os.makedirs(fn)
def readtxt(filename):
    a= open(filename)
    content = a.readlines()
    a.close()
    return content

opt = sys.argv[1]

Dg = "/Users/donglaiwei/Google Drive (donglai@g.harvard.edu)/YouTubeTop-vis/"
#Dc = "/Users/donglaiwei/Desktop/dd/vcg_natural/YouTop200/"
#Dc = "/Users/donglaiwei/Desktop/dl2/youtop/share/"
Dc = "/Users/donglaiwei/Desktop/dd/donglai/YouTop200/db/share/"

#nn = 'movie_trailer/';mn='/seg_all_out/';

videos_v0 = json.load(open(Dg+'video_v0.json'))
names_v0 = videos_v0.keys()
names_v0 = []

videos = json.load(open(Dg+'video.json'))
names_all = [x for x in videos.keys() if x not in names_v0]
nns = np.unique([x[:x.find('/')] for x in videos])

if opt[0] == '5':
    # get stats
    if opt in ['5', '5.1']:
        # drive
        D0 = Dg
        if opt == '5.1':
            # rc
            D0 = Dc
        mns=['/seg_shot_bd/']
        #mns=['/seg_prop/']
        for fn in names_all:
            if fn[:fn.find('/')] in ['movie_trailer']:
                continue
            fn = D0 + fn
            for mn in mns:
                if not os.path.exists(fn + mn):
                    print(fn[fn[:-15].rfind('/')+1:])
                    #gn = Dc + nn + fn[fn.rfind('/'):]
                    #os.system('ls "'+fn+'"')

elif opt[0] == '0':
    if opt == '0': # Google drive: rename folder
        D0 = Dg
        #D0 = Dc
        for fn in names_all:
            if fn[:fn.find('/')] not in ['movie_trailer']:
                continue
            if os.path.exists(D0 + fn + '/seg_all_out/'):
                print(fn)
                shutil.move(D0 + fn + '/seg_all_out/', D0 + fn + '/seg_prop_pf/')
    elif opt == '0.01': # Google drive: remove unlabeled folder
        nn = 'cooking'
        fns = glob(Dc + nn + '/*')
        for fn in fns:
            if not os.path.exists(fn + '/im/'):
                import pdb; pdb.set_trace()
                if not 'Icon' in fn:
                    print(fn)
                    shutil.rmtree(fn)
                    #shutil.move(fn + '/seg_shot_bd/', fn.replace('cooking','music_video/') + '/seg_shot_bd/')
    elif opt == '0.02': # Google drive: check folder
        fns = glob(Dg + nn + '*')
        for fn in fns:
            if not os.path.exists(fn + '/seg_shot_bd/'):
                print(fn)
    elif opt == '0.1': # rename
        mn='/seg_shot_bd/'
        D0 = Dg
        #D0 = Dc
        for fn in names_all:
            # movie_trailer
            #fn2 = fn + '/seg_all_out/'
            # rest
            fn2 = D0 + fn + mn
            if os.path.exists(fn2):
                segs = glob(fn2 + '/*.png')
                if len(segs)>0:
                    sid = segs[0].rfind('/') + 1
                    if segs[0][sid:sid+2] != '_s':
                        print('rename:',segs[0])
                        for seg in segs:
                            shutil.move(seg, fn2 + seg[seg.rfind('_s'):])
    elif opt in ['0.2', '0.3']: # copy file 
        # opt = 0.2
        # drive  -> rc
        mns=['/seg_shot_bd/']
        #mns=['/seg_prop_pf/']
        if opt == '0.3':
            # rc -> drive
            Dg, Dc = Dc, Dg
            mns=['/seg_prop/']
            #mns = ['/im_all.vsvi','/seg_all.vsvi']
        for fn0 in names_all:
            if fn0[:fn0.find('/')] in ['movie_trailer']:
                #pass
                continue
            """
            if fn0[fn0.find('/')+1:] not in ['MFNv-FJFGTg']:
                continue
            """
            fn = Dg + fn0
            for mn in mns:
                if os.path.exists(fn + mn):
                    gn = Dc + fn0
                    if os.path.isdir(fn + mn):
                        num_im = len(glob(gn + mn +'/*.png'))
                        num_im2 = len(glob(fn + mn +'/*.png'))
                    else:
                        num_im = os.path.exists(gn + mn)
                        num_im2 = os.path.exists(fn + mn)
                    if num_im2 > num_im:
                        print(gn,num_im2,num_im)
                        if os.path.isdir(fn + mn):
                            if os.path.exists(gn + mn):
                                shutil.rmtree(gn + mn)
                            shutil.copytree(fn + mn, gn + mn)
                        else:
                            U_mkdir(gn)
                            U_mkdir(fn)
                            shutil.copy(fn + mn, gn + mn)

elif opt[0] == '1': # some video
    if opt == '1':
        data = np.loadtxt(Dg+'music_video/JGwWNGJdvx8/shot.txt').astype(int)
        data = np.unique(data[:] + 1)
        print(','.join([str(x) for x in data]))
    elif opt in ['1.1','1.2']:# count number of seg
        from imageio import imread
        dd = json.load(open('data/video.json'))
        video_names = dd.keys()
        for video_name in video_names:
            video_url = video_name[video_name.find('/')+1:]
            if nn in video_name:
                #print(video_name)
                if opt == '1.1': # count number of instances
                    fns = glob(Dg + video_name + '/seg_shot_bd/*.png')
                    sid = []
                    for fn in fns:
                        sid = np.hstack([sid, np.unique(imread(fn))])
                    print(len(np.unique(sid))-1)
                elif opt == '1.2': # seg_prop
                    # rename and load all
                    if os.path.exists(Dg + video_name + '/seg_prop'):
                        print(video_name)
                        # shutil.rmtree(Dg + video_name + '/seg_prop')
                        # shutil.move(Dg + video_name + '/seg_mask_prop', Dg + video_name + '/seg_prop')
                        """
                        frame_rate = int(np.round(dd[video_name]['fps']))
                        fns = glob(Dg + video_name + '/seg_mask_prop/*.png')
                        for fn in fns:
                            shutil.move() 
                        """
    elif opt == '1.3':
        fns = readtxt('tmp.txt')
        for fn in fns:
            num = len(glob(Dg + fn[:-1] + '/seg_shot_bd/*.png'))
            num2 = len(glob(Dg + fn[:-1] + '/seg_prop/*.png'))
            print(fn[:-1],num,num2)
    elif opt == '1.4':
        fns = readtxt('tmp.txt')
        for fn in fns:
            out = 'zip -r /Users/donglaiwei/Desktop/dd/public/YouTop200/download/' + fn[:-1] + '.zip ' + fn[:-1] + ' -x "*.vsseg"'
            print(out)
