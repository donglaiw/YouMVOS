"""
# add 4 new videos
ls;python scripts/runDownloader.py 0
# video_r2.txt -> json
# manual correction: /n/boslfs02/LABS/lichtman_lab/donglai/youtop2/
"""

import os,sys
sys.path.append('../')
import json
import numpy as np

from T_util import readtxt, U_mkdir, listDiff, writetxt

opt = sys.argv[1]
job_id=0;job_num=1
if len(sys.argv)>3:
    job_id = int(sys.argv[2])
    job_num = int(sys.argv[3])

Do = '/n/boslfs02/LABS/lichtman_lab/donglai/youtop/'
Do = '/n/boslfs02/LABS/lichtman_lab/donglai/youtop2/'
Dr = '/n/pfister_lab2/Lab/vcg_natural/YouTop200/release/'

def getVV(do_new=True):
    jj = json.load(open('data/video.json')) 
    vv = jj.keys()
    bb = ['cooking/2c18PX9acwU','pet/WgoJsBDn1CM','howto/dJTmalNYYa8','education/yZLzLVAUJiU']
    vv = [x for x in vv if not x in bb]
    if do_new:
        vv += ['pet/ozgcKw4MyvY','cooking/7GV-pQ00PCs','howto/G5frRzhSNJ8','education/mnYSMhR3jCI']
    return vv

if opt[0] == '0':# job assignment
    if opt == '0':
        jj = json.load(open('data/video.json')) 
        vv = getVV(False)
        tt = [jj[x]['duration'] for x in vv] 
        sid = np.argsort(tt)
        for i in range(9):
            for x in sid[i::9]:
                print(vv[x])
            print('----')
    elif opt == '0.1': # create folder
        gg = readtxt('data/video_genre.txt')
        for g in gg:
            U_mkdir(Do + g[:-1])
    elif opt == '0.11': # create folder
        # for i in `ls `;do echo `ls $i/|wc -l`; done
        vv = getVV()
        for v in vv:
            U_mkdir(Do + v)
    elif opt == '0.2': # copy image data
        # except 9bZkp7q19f0
        vv = listDiff(getVV(False), ['music_video/9bZkp7q19f0'])
        for v in vv[job_id::job_num]:
            v2 = v.replace('/','_')
            os.system('cp -r %s/%s %s/im/' %(Dr+'JPEGImages', v2, Do + v))
            # seg: need to rename into range(K)
            os.system('cp -r %s/%s %s/seg/' %(Dr+'Annotations/', v2, Do + v))
    elif opt == '0.21': # check number
        from glob import glob
        vv = listDiff(getVV(False), ['music_video/9bZkp7q19f0'])
        for v in vv[job_id::job_num]:
            v2 = v.replace('/','_')
            l0 = len(glob(Dr+'JPEGImages/'+v2+'/*.jpg'))
            l1 = len(glob(Do+v+'/im/*.jpg'))
            l2 = len(glob(Do+v+'/seg/*.png'))
            if l0!=l1 or l0!=l2:
                print('!!!',v,l1,l2,l0)
            #print(v,l1,l2,l0)
    elif opt == '0.22': # output vsvi
        from T_util import arrToStr,writetxt
        from glob import glob
        from imageio import imread
        import vidtool
        from vidtool.view import vsvi_seg
        vv = listDiff(getVV(False), ['music_video/9bZkp7q19f0'])
        for v in vv[job_id::job_num]:
            v2 = v.replace('/','_')
            fns = glob(Dr+'JPEGImages/'+v2+'/*.jpg')
            frame_ids = sorted([int(x[x.rfind('/')+1:-4]) for x in fns])
            im = imread(fns[0])
            frame_size = im.shape
            frame_ids_str = arrToStr(frame_ids)

            # output vsvi
            vsvi_type = 'im'
            vsvi_suf = '_all'
            vsvi_filename = '%05d.jpg'
            output_folder = Do + v
            output_vsvi =  output_folder + '/%s.vsvi' % (vsvi_type + vsvi_suf)
            if not os.path.exists(output_vsvi):
                meta = "%s %s" % (v, vsvi_type)
                image_template = r'.\%s\%s' % (vsvi_type, vsvi_filename)
                output = vsvi_seg % (meta, image_template, 0, \
                                                   image_template, frame_size[1], frame_size[0], \
                                                   frame_ids_str, frame_size[1], frame_size[0], \
                                                   len(frame_ids), meta)
                writetxt(output_vsvi, output)
elif opt[0] == '1':
    # for new video
    # 2022.03.25
    bb = ['cooking_2c18PX9acwU','pet_WgoJsBDn1CM','howto_dJTmalNYYa8','education_yZLzLVAUJiU']
    rr = ['pet_ozgcKw4MyvY','cooking_7GV-pQ00PCs','howto_G5frRzhSNJ8','education_mnYSMhR3jCI']
    if opt =='1':# split
        for nn in ['train','val','test']:
            print(nn)
            vv = readtxt(Dr+'info/split_v1/iccv_%s.txt'%nn)
            for vid,v in enumerate(vv):
                if v[:-1] in bb:
                    print('found:',v[:-1])
                    vv[vid] = rr[[i for i,x in enumerate(bb) if x==v[:-1]][0]]
            writetxt(Dr+'info/cvpr2022_%s.txt'%nn, vv)
    elif opt =='1.1':# scripts
        # extract frames
        # ls scripts/;python scripts/runDownloader.py 0.2
        # json stats
        # ls scripts/;python scripts/runDownloader.py 0.3
        # release JPEG
        # ls scripts/;python scripts/T_release.py 0
        # shot detection
        # ls scripts/;python scripts/runProcessor.py 0
        pass
    elif opt =='1.2':# make folders
        for vv in rr:
            U_mkdir(Dr + 'Annotations/'+vv)
elif opt[0] == '2': # updated mask
    if opt =='2':
        vv = readtxt(Do + '../ha.txt') + ['dfToHzOmwdI\n']
        v2 = [x[-12:] for x in np.hstack([readtxt(Dr + 'info/cvpr2022_val.txt'),readtxt(Dr + 'info/cvpr2022_test.txt')])]
        for v in vv:
            if v in v2:
                print(v[:-1])
elif opt[0] == '3': # zip
    if opt == '3':
        for nn in ['train','val','test'][:1]:
            vvs = readtxt(Dr+'info/cvpr2022_%s.txt'%nn)
            cmd = 'zip -r %s_frame.zip '%nn
            for vv in vvs:
                cmd += '%s '% vv[:-1]
            print(cmd)
