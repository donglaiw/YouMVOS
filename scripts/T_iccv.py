import sys,os
import numpy as np

opt = sys.argv[1]

Dv = '/n/pfister_lab2/Lab/vcg_natural/YouTop200/'
Dvr = Dv + 'release/'
Ds='/n/pfister_lab2/Lab/donglai/YouTop200/db/share/{}/seg_prop_out/seg_%05d.png'
Di=Dv+'{}/frame/image_%05d.png'
Dw='/n/boslfs02/LABS/lichtman_lab/glichtman/public/vcg/youtop-vis/youtube/'

if opt[0] == '-':
    # proofreading: round 3
    # stm 1->6 fps: ls;python scripts/runProcessor.py 2.1
    # copy to release
    # refine seg
    if opt == '-1':
        # visualize stm_out
        # python scripts/runProofreader.py 4.11
        pass

elif opt[0] == '0':
    # split train/val/test
    # bad: data/iccv_bad.txt
    from vidtool import videoTool
    vtool = videoTool()
    vtool.data.setInputVideoJson('data/video.json')
    video_names = vtool.data.video_all_name
    if opt == '0':
        # order by counts
        # ls scripts/;python scripts/runProofreader.py -1
        seg_folder = 'seg_prop_out'
        ll = np.zeros(len(video_names), int)
        for vid,video_name in enumerate(video_names):
            info_txt = vtool.data.FOLDER_DOWNLOAD.format(video_name) + '/%s.txt' % (seg_folder)
            if os.path.exists(info_txt):
                ll[vid] = len(vtool.util.readtxt(info_txt)) 
        yt_bad = [x[:-1] for x in vtool.util.readtxt('data/iccv_bad.txt')]

        # check count
        yt_test = [x[:-1] for x in vtool.util.readtxt('data/iccv_test.txt')]
        ll2 = [ll[i] for i,x in enumerate(video_names) if x in yt_test]
        xx2 = [x for i,x in enumerate(video_names) if x in yt_test]
        # check bad
        yy2 = [x for x in yt_bad if x in yt_test]
        import pdb; pdb.set_trace()
    elif opt == '0.1': # select by Sid's score 
        np.random.seed(12)
        genre = [x[:-1] for x in vtool.util.readtxt('data/video_genre.txt')]
        # yt_bad = [x[:-1] for x in vtool.util.readtxt('data/iccv_bad.txt')]

        result = vtool.util.readtxt('data/result_v0.txt')
        vn = [x[:x.find(' ')] for x in result]
        sc = [float(x[x.find(' ')+1:x.rfind(' ')-1]) for x in result]
        
        val=[]
        test=[]
        train=[]

        vn_all = [x.replace('/','_') for x in video_names]
        for gid in range(10):
            gg = genre[gid]
            # bb = [x.replace('/','_') for x in yt_bad if gg == x[:len(gg)]]
            vv_all = [x for x in vn_all if gg == x[:len(gg)]]
            vv = [x for x in vn if gg  == x[:len(gg)]]
            ss = [sc[i] for i in range(len(vn)) if gg in vn[i]]
            ss2 = np.argsort(ss)
            a = ss2[:7][np.random.permutation(7)[:2]]
            b = ss2[7:14][np.random.permutation(7)[:2]]
            c = ss2[14:][np.random.permutation(len(ss2[14:]))[:2]]
            val += [vv[a[0]]] + [vv[b[0]]] + [vv[c[0]]]
            test += [vv[a[1]]] + [vv[b[1]]] + [vv[c[1]]]
            train += [x for x in vv_all if (x not in test and x not in val)]
        vtool.util.writetxt('data/iccv_train.txt', train)
        vtool.util.writetxt('data/iccv_val.txt', val)
        vtool.util.writetxt('data/iccv_test.txt', test)
    elif opt == '0.2': # txt -> js
        Dw='/n/pfister_lab2/Lab/public/YouTop200/'
        for nn in ['train','val','test']:
            video_names = '","'.join([x[:-13]+'/'+x[-12:-1] for x in vtool.util.readtxt('data/iccv_%s.txt'%nn)])
            print(video_names)
            vtool.util.writetxt(Dw+'js/video_%s.js'%nn, 'var video_name=["'+video_names+'"];')

elif opt[0] == '1': # count number of instances
    if opt == '1':
        # num = 7;cn = 'scripts/runProofreader.py -1'
        pass
