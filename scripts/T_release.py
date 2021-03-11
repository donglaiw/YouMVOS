import os,sys,shutil
import json
import numpy as np
sys.path.append('../')
from T_util import U_mkdir,writetxt,readtxt
from imageio import imread,imwrite
from glob import glob

opt = sys.argv[1]
job_id=0;job_num=1;
if len(sys.argv)>3:
    job_id = int(sys.argv[2])
    job_num = int(sys.argv[3])

Dv = '/n/pfister_lab2/Lab/vcg_natural/YouTop200/'
Dvr = Dv + 'release/'
Ds='/n/pfister_lab2/Lab/donglai/YouTop200/db/share/{}/seg_prop_out/seg_%05d.png'
Di=Dv+'{}/frame/image_%05d.png'
Dw='/n/boslfs02/LABS/lichtman_lab/glichtman/public/vcg/youtop-vis/youtube/'

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
        video_names=['product/tQANVXppDPE','education/uyMtsyzXWd4','product/8OJdwuvZWrI','sports/8b0ubLO2MUE','cooking/u6TFP_r2oA8','kid/do6EgKG_YUo','sports/_6VeZAZdff0','sports/4rp2aLQl7vg','sports/zl7A-Vbe5N8','cooking/ct5Q73pgVMA','tv/Z4SXxxUnq0U','tv/zgIib_Uj1T4','product/wkuDpfiDPYs']
        video_names = ["sports/NzYtFLpJrQU","music_video/7PCkvCPvDXk","product/dfToHzOmwdI","movie_trailer/EcxBrTvLbBM","howto/qsxcVsFDDoA","howto/GibMs1kod2Y","tv/_yl2fV6SM_8","tv/746NhRSrNOY"]
        video_names = ['sports/2O7K-8G2nwU','product/JQk56_ZJEOo','tv/izh-j8KUYjs',"cooking/ScgkiTz4nPk","kid/xqvN9yJeyO0","howto/wk7qkgS-TTg","tv/K_dFhEeuCtM"]
        video_names = ["music_video/pRpeEdMmmQ0","cooking/iUtLMkLhUKY","tv/0oPa3GJJDDA","product/4RtNDHPq2V4"]
        video_names = ["product/4RtNDHPq2V4"]
        video_names = ['cooking/iUtLMkLhUKY','howto/wk7qkgS-TTg']
        do_rm = True
        do_rm = False
        for video_name in video_names:
            print(video_name)
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
            if do_rm:
                if os.path.exists(Do2):
                    print('rm %s/*.png'%Do2)
            else:
                for i in range(0, num_im, step)[job_id::job_num]:
                    sn = Do2 + '/%05d.png' % (1+i)
                    if True: #not os.path.exists(sn):
                        sn2 = Ds2 % (i//step)
                        if os.path.exists(sn2):
                            shutil.copyfile(sn2, sn)
                        else:
                            imwrite(sn, black)
    elif opt == '0.2': # check number
        Do = Dv + 'release/Annotations/'
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
            num_6fps = (num_im + step - 1) // step
            num = len(glob(Do2 + '/*.png'))
            if num != num_6fps:
                print(num, num_6fps)
                import pdb; pdb.set_trace()

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
        train = readtxt('data/yt_val.txt')
        train = readtxt('data/yt_test.txt')
        kk = 'movie_trailer'
        kk = 'music_video'
        kk = 'cooking'
        kk = 'education'
        kk = 'pet'
        kk = 'tv'
        kk = 'sports'
        kk = 'kid'
        kk = 'howto'
        kk = 'product'
        kk = ''
        pp = 'https://rhoana.rc.fas.harvard.edu/YouTop200/proofread/'
        pp = 'https://lichtman.rc.fas.harvard.edu/vcg/youtop-vis/youtube/proofread/'
        ss = '_seg.html?fps=%d&pref=stm_out_&suf=_shot_out'
        for x in train :
            if kk+'/' in x:
                #print(x[:-1])
                y = x[:x.find('/')] + '/test/' + x[x.find('/')+1:-1]
                print(pp + y + '_shot_out.html')
                #print(pp + y + ss % getVideoFrameStep(int(np.round(videos[x[:-1]]['fps']))))
elif opt[0] == '2':
    if opt == '2':
        fn0 = Dvr + '../data/video.json'
        fn = Dvr + 'info/video.json'
        videos = json.load(open(fn0))
        kks = list(videos.keys())
        for kk in kks:
            videos[kk.replace('/','_')] = videos[kk]
            del videos[kk]
        json.dump(videos, open(fn,'w'))

elif opt[0] == '3':
    from vidtool import videoTool
    vtool = videoTool(job_id, job_num)
    Do = 'db/Tanav/'
    vtool.data.setInputVideoJson('data/video.json')
    video_names = vtool.data.video_all_name
    video_names = [x[:x.find(',')] for x in vtool.util.readtxt('data/video.txt')]

    if opt == '3': # avg view
        sn = Do + 'genre_view.txt'
        if False:# os.path.exists(sn):
            import pdb; pdb.set_trace()
            stat = np.loadtxt(sn).astype(int)
        else:
            stat = np.zeros(200, int)
            for vid, video_name in enumerate(video_names):
                video_url = video_name[video_name.rfind('/')+1:]
                stat[vid] = vtool.util.getVideoViews(video_url)
            import pdb; pdb.set_trace()
            np.savetxt(sn, stat.reshape(10,-1).mean(axis=1),'%d')
        print(stat.mean())
        print(np.argsort(-stat.reshape(10,-1).mean(axis=1)))
    elif opt == '3.01': # avg view
        genres = [x[:x.find('/')] for x in video_names[::20]]
        print(genres)
        sn = Do + 'genre_name.txt'
        vtool.util.writetxt(sn, genres)
    elif opt == '3.1': # avg shots
        stat = np.zeros(200, int)
        for vid, video_name in enumerate(video_names):
            sn = Dvr + 'Annotations/' +video_name.replace('/','_')+'/shot.txt'
            dd = np.loadtxt(sn).astype(int)
            stat[vid] = (dd[1:,-1]!=2).sum()
        np.savetxt(Do + 'genre_shots.txt', stat.reshape(10,-1).mean(axis=1),'%d')
        print(stat.mean())
    elif opt == '3.11': # avg shots
        stat = np.zeros(200, int)
        for vid, video_name in enumerate(video_names):
            sn = Dvr + 'Annotations/' +video_name.replace('/','_')+'/shot.txt'
            dd = np.loadtxt(sn).astype(int)
            stat[vid] = (dd[1:,-1]==2).sum()
        np.savetxt(Do + 'genre_shots_invalid.txt', stat.reshape(10,-1).mean(axis=1),'%d')
        print(stat.mean())
    elif opt == '3.12': # avg shots
        stat = np.zeros(200, int)
        for vid, video_name in enumerate(video_names):
            sn = Dvr + 'Annotations/' +video_name.replace('/','_')+'/shot.txt'
            dd = np.loadtxt(sn).astype(int)
            step = dd[0,2]
            dd = dd[dd[:,-1]==0]
            stat[vid] = ((dd[:,1]-dd[:,0])//step+1).sum()
        import pdb; pdb.set_trace()
        # 324938
        print(stat.sum())


    elif opt == '3.2': # #instance for test
        video_names = [x[:-1] for x in vtool.util.readtxt('data/split/yt_test.txt')]
        stat = np.zeros(len(video_names), int)
        for vid, video_name in enumerate(video_names):
            sn = Dv + video_name + '/seg_prop_out.txt'
            if os.path.exists(sn):
                dd = vtool.util.readtxt(sn)
                stat[vid] = len(dd)
        print(stat)
        print(stat.min())





    elif opt == '3.21': # gif for test
        nn = 'val'
        video_names = '","'.join([x[:-1] for x in vtool.util.readtxt('data/yt_%s.txt'%nn)])
        print(video_names)
        vtool.util.writetxt(Dw+'js/video_%s.js'%nn, 'var video_name=["'+video_names+'"];')
    elif opt == '3.22': # test/val overlap
        test = vtool.util.readtxt('data/yt_test.txt')
        test = vtool.util.readtxt('data/yt_val_bad.txt')
        val = vtool.util.readtxt('data/yt_val.txt')
        print([x for x in val if x in test])
    elif opt == '3.23': # create train
        test = [x[:-1] for x in vtool.util.readtxt('data/yt_test.txt')]
        val = [x[:-1] for x in vtool.util.readtxt('data/yt_val.txt')]
        train = [x for x in video_names if (x not in test) and (x not in val)]
        vtool.util.writetxt('data/yt_train.txt', train)

    elif opt == '3.24': # count test shots
        test = [x[:-1] for x in vtool.util.readtxt('data/split/yt_test.txt')]
        ss = np.zeros(len(test), int)
        oo = np.zeros(len(test), int)
        for i in range(len(test)):
            tmp = np.loadtxt(Dvr + 'Annotations/' + test[i].replace('/','_') +'/shot.txt').astype(int) 
            ss[i] = (tmp[:,-1]==0).sum()
            tmp = readtxt(Dv + test[i] + '/seg_prop_out.txt')
            oo[i] = len(tmp)
        print(ss.sum())
        print(oo.sum())

    elif opt == '3.3': # get filename
        numK = 50
        out_list = []
        for vid, video_name in enumerate(video_names): 
            # list of the image index for each objects
            print(vid)
            stat = readtxt(Dv + video_name + '/seg_prop_out.txt')
            if len(stat) > 0:
                tmp = [] 
                for i in range(len(stat)):
                    val = np.array([int(x) for x in stat[i][:-1].split(',')])
                    step = np.unique(np.round(np.linspace(0, len(val)-2, numK))).astype(int)
                    tmp += [video_name + ' %d %d' %(val[0], val[x+1]) for x in step]
                out_list += tmp
        writetxt('db/fig3/name.txt', out_list)
    elif opt == '3.31': # compute shape stats
        from skimage.measure import perimeter
        out = readtxt('db/fig3/name.txt')
        stat=np.zeros(len(out))
        for i,oo in enumerate(out):
            if i % 100 ==0:
                print(i)
            tmp = oo[:-1].split(' ') 
            seg = imread(Ds.format(tmp[0])%int(tmp[2])) == int(tmp[1])
            stat[i] = perimeter(seg) / np.sqrt(seg.sum())
        np.savetxt('db/fig3/stat.txt', stat, '%.3f')
    elif opt == '3.32': # sample 1000 objects
        # range: 0, \sqrt(pi)
        out = readtxt('db/fig3/name.txt')
        stat = np.loadtxt('db/fig3/stat.txt')
        stat[stat>0] = 1. / stat[stat>0] 
        # bins
        num_bin = 10
        num_seg = 50
        thres = np.percentile(stat,[1,99])
        thres_bin = np.linspace(thres[0],thres[1], num_bin + 1)
        thres_bin[0] = 0
        thres_bin[-1] = stat.max()
        np.random.seed(1234)
        dd = [None] * num_bin
        import pdb; pdb.set_trace()
        for i in range(num_bin):
            sid = np.where((stat>thres_bin[i]) * (stat<=thres_bin[i+1]))[0]
            nn = [out[x][:out[x].find(' ')] for x in sid]
            ui,ud = np.unique(nn, return_index=True) 
            dd[i] = sid[np.random.permutation(ud)[:num_seg]]
        np.savetxt('db/fig3/shape_%d.txt'%(num_bin*num_seg), np.hstack(dd), '%d')
    elif opt == '3.33': # generate mask: visual check
        stat = np.loadtxt('db/fig3/stat.txt')
        Do = Dw + 'tmp/fig3/%d.png'
        out = readtxt('db/fig3/name.txt')
        sid = np.loadtxt('db/fig3/shape_500.txt').astype(int)
        for i in range(len(sid)):
            tmp = out[sid[i]][:-1].split(' ')
            print(tmp, stat[sid[i]])
            """
            fps = vtool.data.video_all_info[tmp[0]]['fps']
            step = vtool.util.getVideoFrameStep(int(np.round(fps))) 
            im = imread(Di.format(tmp[0])%(1+step*int(tmp[2])))
            seg = (imread(Ds.format(tmp[0])%int(tmp[2])) == int(tmp[1])).astype(np.uint8)
            imwrite(Do%i, vtool.util.visSeg(im[::4,::4], seg[::4,::4]))
            """
    elif opt in ['3.34','3.35','3.36','3.37','3.38','3.341']: # output for label
        sel=[452,454,455,457,458,459,461,463,468,469,418,416,414,415,411,410,407,402,401,400,363,365,367,368,370,372,373,374,378,381,331,332,328,327,326,325,323,322,320,319,272,273,274,276,277,280,281,283,284,285,236,234,232,230,229,226,225,221,220,216,165,166,169,172,176,179,182,183,184,191,141,140,139,137,136,134,131,129,126,122,76,77,78,81,84,86,88,90,93,95,45,48,49,39,37,32,24,23,22,15]
        out = readtxt('db/fig3/name.txt')
        sid = np.loadtxt('db/fig3/shape_500.txt').astype(int)
        if opt == '3.341':
            stat = np.loadtxt('db/fig3/stat.txt')
            import pdb; pdb.set_trace()
            for i in range(len(sel)):
                tmp = out[sid[sel[i]]][:-1].split(' ')
                print(1.0/stat[sid[i]])

        elif opt == '3.34':
            Do = Dw + 'tmp/fig3/output/%d.png'
            for i in range(len(sel)):
                tmp = out[sid[sel[i]]][:-1].split(' ')
                fps = vtool.data.video_all_info[tmp[0]]['fps']
                step = vtool.util.getVideoFrameStep(int(np.round(fps))) 
                shutil.copy(Di.format(tmp[0])%(1+step*int(tmp[2])), Do%i)
        elif opt == '3.35': # output for paper
            Do = Dw + 'tmp/fig3/color/%d.png'
            for i in range(len(sel)):
                tmp = out[sid[sel[i]]][:-1].split(' ')
                fps = vtool.data.video_all_info[tmp[0]]['fps']
                step = vtool.util.getVideoFrameStep(int(np.round(fps))) 
                im = imread(Di.format(tmp[0])%(1+step*int(tmp[2])))[::4,::4]
                seg = (imread(Ds.format(tmp[0])%int(tmp[2])) == int(tmp[1])).astype(np.uint8)[::4,::4]
                out_im = vtool.util.visSeg(im, seg)*0.5
                for c in range(3):
                    out_c = out_im[:,:,c]
                    im_c = im[:,:,c]
                    out_c[seg>0] = im_c[seg>0]
                imwrite(Do%i, out_im)
        elif opt == '3.36': # output for seg
            Do = Dw + 'tmp/fig3/pipeline_seg/%d.png'
            for i in range(len(sel)):
                tmp = out[sid[sel[i]]][:-1].split(' ')
                seg = (imread(Ds.format(tmp[0])%int(tmp[2])) == int(tmp[1])).astype(np.uint8)*255
                imwrite(Do%i, seg)

        elif opt == '3.37': # manual
            Do = Dw + 'tmp/fig3/pipeline_r3/%d.png';
            for i in range(100):
                seg = (imread(Do%i)>0).astype(np.uint8)*255
                imwrite(Do%i, seg)
        elif opt == '3.38': # manual
            from skimage.measure import perimeter
            sc = np.zeros(100)
            for i in range(100):
                tmp = out[sid[sel[i]]][:-1].split(' ')
                seg = (imread(Ds.format(tmp[0])%int(tmp[2])) == int(tmp[1])).astype(np.uint8)
                sc[i] = (4*np.pi*(seg>0).sum())/(perimeter(seg)**2)
            print(sc)
            print(','.join(['%.04f'%x for x in sc]))



    elif opt == '3.4': # instance count
        pp = 'https://lichtman.rc.fas.harvard.edu/vcg/youtop-vis/youtube/proofread/'
        genres = [x[:x.find('/')] for x in video_names[::20]]
        for x in genres:
            print(pp + x + '/test/dsp_character.html')
    elif opt == '3.41': # instance count
        for x in video_names:
            print(x)

    # fig.4
    elif opt == '3.5': # instance count
        from glob import glob
        nns = ['feats','positions']
        for nn in nns:
            same=[None]*185
            cross=[None]*185
            fs = glob('db/anirudh/%s/'%nn+'*same.txt')
            fc = glob('db/anirudh/%s/'%nn+'*cross.txt')
            for fid in range(185):
                same[fid] = np.loadtxt(fs[fid])
                cross[fid] = np.loadtxt(fc[fid])
            np.savetxt('db/anirudh/same_%s.txt'%nn, np.hstack(same), '%.4f')
            np.savetxt('db/anirudh/cross_%s.txt'%nn, np.hstack(cross), '%.4f')
    # fig 1
    elif opt == '3.6': # instance count
        from skimage.color import label2rgb
        clr = np.array(['black', 'green', 'blue', 'red', 'magenta', 'cyan', 'yellowgreen', 'red', 'pink', 'indigo', 'green'])
        for i in range(4):
            seg = imread('db/fig1/_s%d.png'%i)
            if i==2:
                import pdb; pdb.set_trace()
                seg[seg==2]=3
            out = (255.*label2rgb(seg, colors=clr)).astype(np.uint8)
            imwrite('db/fig1/out_%d.png'%i, out)
