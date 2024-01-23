import sys,os
import numpy as np
# sa vis

opt = sys.argv[1]

Dv = '/n/pfister_lab2/Lab/vcg_natural/YouTop200/'
Dvr = Dv + 'release/'
Ds='/n/pfister_lab2/Lab/donglai/YouTop200/db/share/{}/seg_prop_out/seg_%05d.png'
Di=Dv+'{}/frame/image_%05d.png'
Dw='/n/boslfs02/LABS/lichtman_lab/glichtman/public/vcg/youtop-vis/youtube/'

from vidtool import videoTool
vtool = videoTool()
vtool.data.setInputVideoJson('data/video_r2.json')
#vtool.data.setInputVideoJson('data/video.json')
video_names = vtool.data.video_all_name
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
    video_names = vtool.data.video_all_name
    video_genres = [video_name[:video_name.rfind('/')] for video_name in video_names]
    video_genre, video_id = np.unique(video_genres, return_inverse = True)
    if opt == '1': # get seg stat
        # ls */*/seg_prop_out.txt|wc -l
        # num = 7;cn = 'scripts/runProofreader.py -1'
        # ls;python scripts/runProofreader.py -2
        pass
    elif opt == '1.1': # count number of instances and masks
        fn = 'seg_prop_out'
        num = np.zeros(200) # obj
        num2 = np.zeros(200) # mask
        num3 = [None] * 200 # switch
        for vid,video_name in enumerate(video_names):
            print(video_name)
            vtool.data.setVideoInfo(video_name)
            output_txt = vtool.data.FOLDER_DOWNLOAD.format(video_name) + '/%s.txt' %(fn)
            if os.path.exists(output_txt):
                data = vtool.util.readtxt(output_txt)
                num[vid] = len(data)
                num2[vid] = sum([x.count(',') for x in data]) 
                tmp = np.array([int(y) for y in x[x.find(',')+1:].split(',')]) for x in data])
                num3[vid] = sum([x.count(',') for x in data]) 
        #print([video_names[x] for x in np.where(num>10)[0]])
        #print([video_names[x] for x in np.where(num==1)[0]])
        import pdb; pdb.set_trace()

elif opt[0] == '2': # supp
    from vidtool import videoUtil as vutil
    if opt == '2':
        import glob
        import shutil
        fns = sorted(glob.glob(Dvr + 'Annotations/music_video_9bZkp7q19f0/*.png'))
        for i,fn in enumerate(fns):
            shutil.copy(fn, 'db/gangnum/%04d.png'%i)
    # one full video
    elif opt == '2.1':
        # add the sunglass pasrt
        from imageio import imread,imwrite
        Do = 'db/gangnum_seg_pf/'
        #im = imread(Do+'_s0034.png')
        for i in range(34):
            imwrite(Do+'_s%04d.png'%i, np.ones([720,1280], np.uint8))
    elif opt == '2.11':
        from imageio import imread,imwrite
        from scipy.ndimage import zoom
        Di = 'db/gangnum_seg_pf/_s%04d.png'
        Do = 'db/gangnum_seg_pf_out/%04d.png'
        ind = [190, 770, 790, 645, 1130, 1190, 1285, 1280, 1225, 680]
        #for i in range(1512):
        for i in ind:
            im = imread(Dvr + 'JPEGImages/music_video_9bZkp7q19f0/%05d.jpg'%(1+i*4))
            if os.path.exists(Di%i):
                seg = imread(Di%i)
                im = vutil.visSeg(im,seg)
            imwrite(Do%i, zoom(im, [0.5,0.5,1], order=1))
    elif opt == '2.12':
        from imageio import imread,imwrite
        from scipy.ndimage import zoom
        Do = 'db/gangnum_im/%04d.png'
        for i in range(1512):
            im = imread(Dvr + 'JPEGImages/music_video_9bZkp7q19f0/%05d.jpg'%(1+i*4))
            imwrite(Do%i, zoom(im, [0.5,0.5,1], order=1))
    elif opt == '2.13':# new mask [Tanav]
        from imageio import imread,imwrite
        from scipy.ndimage import zoom
        Dseg = 'db/gangnum_v2/_s%04d.png'
        Dim = 'db/gangnum_im/%04d.png'
        Do = 'db/gangnum_v2_out/%04d.png'
        job_id = int(sys.argv[2])
        job_num = int(sys.argv[3])
        ind = range(1512)[job_id::job_num]
        #ind = [190, 770, 790, 645, 1130, 1190, 1285, 1280, 1225, 680]
        for i in range(len(ind)):
            ii = ind[i]
            if not os.path.exists(Do%ii):
                im = imread(Dim % ii)
                seg = imread(Dseg % ii)[::2, ::2]
                im = vutil.visSeg(im,seg)
                imwrite(Do % ii, im)

    # single image with mask on
    # https://lichtman.rc.fas.harvard.edu/vcg/youtop-vis/youtube/vis_seg.html
    elif opt == '2.2':
        nn = vutil.readtxt('db/dataset/example.txt')
        #print(','.join(['"'+x[:-1]+'"' for x in nn]))
        nn2 = [x[:x.find('/')] for x in nn[::20]]
        print(', '.join(nn2))
    # dataset image + image-seg
    elif opt == '2.3':
        from imageio import imread,imwrite
        from scipy.ndimage import zoom
        nns = ['music_video/nfWlot6h_JM','kid/KYniUCGPGLs','movie_trailer/BHi-a1n8t7M','cooking/3nUKwvFsjA4','sports/wgVOgGLtPtc','tv/0oBodJHX1Vg','howto/14mRmD8zHOk','education/uyMtsyzXWd4','pet/AaDBwFnDUZY','product/Mm0NvlXdz4A']
        Do = 'db/iccv_dataset/'
        vtool = videoTool(0, 1)
        vtool.data.setInputVideoJson('data/video.json')
        job_id = int(sys.argv[2])
        job_num = int(sys.argv[3])
        for nn in nns[job_id::job_num]:
            vtool.data.setVideoInfo(nn)
            nn2 = nn.replace('/', '_')
            fps = vtool.data.video_frame_step
            Do2 = Do + nn2 + '/'
            vutil.mkdir(Do2)
            # get 1000 frames
            Dim = Dvr + 'JPEGImages/%s/%05d.jpg'
            Dseg = Dvr + 'Annotations/%s/%05d.png'
            for i in range(100,1100):
                #print(nn,i)
                im = imread(Dim%(nn2, 1 + i * fps))
                seg = imread(Dseg%(nn2, 1 + i * fps))
                im = np.hstack([im, vutil.visSeg(im,seg)])
                imwrite(Do2 + '%04d.png'%i, zoom(im, [0.5,0.5,1], order=1))
    elif opt == '2.31':
        nns = ['music_video/nfWlot6h_JM','kid/KYniUCGPGLs','movie_trailer/BHi-a1n8t7M','cooking/3nUKwvFsjA4','sports/wgVOgGLtPtc','tv/0oBodJHX1Vg','howto/14mRmD8zHOk','education/uyMtsyzXWd4','pet/AaDBwFnDUZY','product/Mm0NvlXdz4A']
        Do = 'db/iccv_dataset/'
        vtool = videoTool(0, 1)
        vtool.data.setInputVideoJson('data/video.json')
        for nn in nns:
            vtool.data.setVideoInfo(nn)
            fps = vtool.data.video_frame_step
            fps = 6 if fps==4 else 5
            nn2 = nn.replace('/', '_')
            #print(nn,fps)
            print('ffmpeg -start_number 100 -f image2 -framerate '+str(fps)+' -i '+nn2+'/%04d.png -c:v libx264 -preset veryslow -crf 18 -pix_fmt yuv420p '+nn2+'.mp4')
    # result comparison
    elif opt == '2.4':
        from imageio import imread,imwrite
        from glob import glob
        D0 = '/n/pfister_lab2/Lab/public/YouTop200/seg_ds/'
        #nns = glob(D0 + 'Orig_MT/*')
        #nns = [x[x.rfind('/')+1:] for x in nns]
        nns = ['music_video_7PCkvCPvDXk','movie_trailer_BHi-a1n8t7M','tv_qVMW_1aZXRk','education_d0nfzeLXuyY']
        Do = 'db/iccv_comparison/'
        vtool = videoTool(0, 1)
        vtool.data.setInputVideoJson('data/video.json')
        job_id = int(sys.argv[2])
        job_num = int(sys.argv[3])
        for nn2 in nns[job_id::job_num]:
            nn = nn2[:-12] + '/' + nn2[-11:]
            vtool.data.setVideoInfo(nn)
            fps = vtool.data.video_frame_step
            Do2 = Do + nn2 + '/'
            vutil.mkdir(Do2)
            # get 1000 frames
            Da = D0 + 'Orig_MT/%s/results_%05d.png'
            Db = D0 + 'iccv_sub/%s/results_%05d.png'
            for i in range(0,1000):
                #print(nn,i)
                ima = imread(Da%(nn2, 1 + i * fps))
                imb = imread(Db%(nn2, 1 + i * fps))
                imwrite(Do2 + '%04d.png'%i, np.hstack([ima, imb]))
    elif opt == '2.41':
        nns = ['music_video/7PCkvCPvDXk','movie_trailer/BHi-a1n8t7M','tv/qVMW_1aZXRk','education/d0nfzeLXuyY']
        Do = 'db/iccv_dataset/'
        vtool = videoTool(0, 1)
        vtool.data.setInputVideoJson('data/video.json')
        for nn in nns:
            vtool.data.setVideoInfo(nn)
            fps = vtool.data.video_frame_step
            fps = 6 if fps==4 else 5
            nn2 = nn.replace('/', '_')
            #print(nn,fps)
            print('ffmpeg -f image2 -framerate '+str(fps)+' -i '+nn2+'/%04d.png -c:v libx264 -preset veryslow -crf 18 -pix_fmt yuv420p '+nn2+'.mp4')
 
elif opt[0] == '3': # rebuttal
    if opt == '3':
        import shutil
        num = 1512
        for i in range(50):
            shutil.copy('%04d.png'%(i*30),'shray/%04d.png'%i)
        pass
