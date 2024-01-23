import os,shutil,sys,json
from glob import glob
import numpy as np
from vidtool import videoUtil as vutil
from imageio import imread, imwrite

opt = sys.argv[1]
Dl2 = '/n/boslfs02/LABS/lichtman_lab/donglai/youtop/'
Dv = '/n/pfister_lab2/Lab/vcg_natural/YouTop200/release/'
Dw = '/n/pfister_lab2/Lab/public/youtop200/'
#Dw = '/n/boslfs02/LABS/lichtman_lab/glichtman/public/vcg/youtop-vis/youtube/'
def getFrameStep(fps):
    fps = int(np.round(fps))
    if fps in [25,30]:
        frame_step = 5
    elif fps in [24]:
        frame_step = 4
    elif fps in [27]:
        frame_step = 3
    else:
        import pdb; pdb.set_trace()
    return frame_step

def str2Arr2(t, opt):
    if '-' in t:
        t2 = t.split('-')
        if opt == 'first':
            out = [int(t2[0].strip())]
        else:
            mm = [int(t2[0].strip()), int(t2[1].strip())]
            out = [x for x in range(min(mm), max(mm)+1)]
    else:
        out = [int(t.strip())]
    return out

def str2Arr(input_str, opt='all', arr=True):
    tmp = input_str.split(',')
    out = len(tmp)*[None]
    for i,t in enumerate(tmp):
        if '_' in t:
            tt = t.split('_')
            if opt =='first':
                out[i] = str2Arr2(tt[0], opt)
            else:
                out[i] = vutil.flatList([str2Arr2(x) for x in tt], False)
        else:
            out[i] = str2Arr2(t, opt)
    if arr:
        out = list(np.hstack(out))
    return out


if opt[0] == '0':
    # change folder structure
    D0 = '/n/boslfs02/LABS/lichtman_lab/glichtman/public/vcg/youtop-vis/youtube/proofread/'
    genres = [x[x.rfind('/')+1:] for x in glob(D0+'../frame_ds/*')]
    if opt == '0':
        nns = ['html','result']
        for nn in nns:
            vutil.mkdir(D0 + nn + '/')
            for genre in genres:
                D1 = D0 + nn + '/' + genre + '/'
                vutil.mkdir(D1)
                if nn == 'html':
                    fns = glob(D0+genre+'/test/*.html')
                elif nn == 'result':
                    fns = glob(D0+genre+'/saved/*.js')
                for fn in fns:
                    fn_b = fn[fn.rfind('/')+1:]
                    shutil.copy(fn, D1+fn_b)
    elif opt == '0.1':
        nn = 'result/'
        for genre in genres:
            D1 = D0 + nn + genre + '/'
            D2 = D0 + genre + '/'
            os.system('mv '+D1+'*.js '+D2)
    elif opt == '0.2':
        vvs = vutil.readtxt('data/video_old.txt') 
        for vv2 in vvs:
            vv = vv2[:-1]
            vutil.rm(D0 + vv + '_shot_out.html')
            vutil.rm(D0 + vv + '_shot.html')
            vutil.rm(D0 + vv + '_shot.js')
            if os.path.exists(D0 + vv + '_shot_out.js'):
                shutil.move(D0 + vv + '_shot_out.js', D0 + vv + '_shot.js')
    elif opt == '0.3':
        for g in genres:
            vutil.mkdir('db/round3/'+g, '')


elif opt[0] == '1':# proofread dataset
    if opt == '1':
        D0 = '/n/pfister_lab2/Lab/vcg_natural/YouTop200/release/info/'
        vv = []
        for nn in ['train','val','test']:
            vv = vv + vutil.readtxt(D0 + 'cvpr2022_%s.txt'%nn)
        print(len(vv))
        ui,uc=np.unique(vv, return_counts=True)
        print(uc.max())

        oo = [None]*2
        for mid,mm in enumerate(['video_rest','video_done']):
            oo[mid] = vutil.readtxt('data/%s.txt'%mm)
            print(len(oo[mid]))
            print([x for x in oo[mid] if x.replace('/','_') not in vv])
        print([x for x in oo[0] if x in oo[1]])
        qq = [x.replace('/','_') for x in oo[0]+oo[1]]

        print([x for x in vv if x not in qq])
        """
        print(len(np.unique(oo[0]+oo[1])))
        ui,uc=np.unique(oo[0]+oo[1], return_counts=True)
        print([ui[x] for x in np.where(uc>1)])
        """
    elif opt == '1.1':# sort by genre
        for mm in ['video_rest','video_done']:
            oo = sorted(vutil.readtxt('data/%s.txt'%mm))
            vutil.writetxt('data/%s.txt'%mm, oo)
elif opt[0] == '2':# copy over files
    if opt == '2':
        sys.path.append('vidtool')
        from htmlGenerator import getVsvi 
        from vidtool import videoTool
        vtool = videoTool('data/video_rest.txt','data/param.txt')
        nns=['cooking','education','howto','movie_trailer','kid','music_video']
        #nns=['pet','product','sports','tv']
        nns=['cooking']
        mm ='todo'
        #mm ='todo2'
        info = json.load(open('data/video_rest.json'))
        Dv2 = Dv + 'Annotations/'
        opts=['','first','all']
        suf = ''
        suf = '_add'
        cmd_file = 'tmp_detectron2.sh'
        vid = 0
        for nn in nns:
            vvs = vutil.readtxt('db/round3/%s/%s.txt'%(nn,mm))
            for vv in vvs:
                tmp = vv.split(';')
                sn = Dl2 + nn + '/' +tmp[0]+'_imr3%s.vsvi'%suf
                sn2 = Dl2 + nn + '/' +tmp[0]+'_segr3%s.vsvi'%suf
                if True :# not os.path.exists(sn2):
                    frame_step = getFrameStep(info[nn+'/'+tmp[0]]['fps'])
                    fns = []
                    for i in range(1,3):
                        if len(tmp[i]) > 0 and tmp[i] != '\n':
                            fns += str2Arr(tmp[i], opts[i])
                    fns = np.array(fns) * frame_step + 1
                    if suf == '_add':
                        # minus done ones
                        ff = vutil.readtxt(Dl2 + nn + '/' +tmp[0]+'_imr3.vsvi')
                        fns_d = np.array([int(x) for x in ff[20][ff[20].find(':')+3:-3].split(',')])
                        fns = fns[np.in1d(fns, fns_d, invert=True)]
                    print(nn + '/' + tmp[0] + ',%d'%len(fns))
                    # copy frames
                    Do = Dl2 + nn + '/' +tmp[0]+'_segr3'+suf+'/%03d.png'
                    vutil.mkdir(Do)
                    for fid, fn in enumerate(fns):
                        if not os.path.exists(Do%fid):
                            shutil.copy(Dv2 + '%s_%s/%05d.png'%(nn,tmp[0],fn), Do%fid)
                    # make im vsvi
                    vsvi = getVsvi('image round3', r'.\im\%05d.jpg', vutil.converArrToStr(fns), info[nn+'/'+tmp[0]]['size'][::-1])
                    vutil.writetxt(sn, vsvi)
                    # detectron2 cmd
                    if vid == 0:
                        if os.path.exists(cmd_file):
                            os.remove(cmd_file)
                        vutil.writetxt(cmd_file, ['#/bin/bash'])
                        os.chmod(cmd_file, 0o755)
                    output_template = Dl2 + nn + '/' +tmp[0]+'_detectron_r3'+suf+'/%05d.png'
                    frame_template = Dv + 'JPEGImages/'+ nn + '_' +tmp[0]+'/%05d.jpg'
                    vtool.processor.segDetectron2(fns, frame_template, output_template, cmd_file)
                    # make seg vsvi
                    vsvi = getVsvi('seg round3', r'.\%s_detectron_r3'% tmp[0] + suf + r'\%05d.png', vutil.converArrToStr(fns), info[nn+'/'+tmp[0]]['size'][::-1])
                    vutil.writetxt(sn2, vsvi)
                    vid += 1

elif opt[0] == '3':# handcrafted
    if opt =='3':
        #vvs = vutil.readtxt('data/cvpr2022_final.txt')
        vvs = [x.replace('/','_') for x in vutil.readtxt('data/video_bad.txt')]
        for vv in vvs:
            print(vv[:-1])
            gn,vn = vv[:-13],vv[-12:-1]
            Do = Dv+'Annotations/%s/'%(vv[:-1])
            fns = glob(Do + '*.png')
            for fn in fns:
                im = imread(fn)
                # rotate seg
                if im.shape[0] > im.shape[1] and vv[:-1] not in ['pet_ZkGTX3PUSHc']:
                    print(fn)
                    import pdb; pdb.set_trace()
                    imwrite(fn, im.transpose())
                """
                elif im.shape[0] == 1280:
                    print(fn)
                    imwrite(fn, im.transpose())
                elif im.shape[0] != 720 and vv[:-1] not in ['movie_trailer_KK8FHdFluOQ','kid_yrynT4T55Xc','tv_JDjSHmQz1U0','music_video_bnVUHWCynig','kid_do6EgKG_YUo','tv_BJXq83_GvY8','product__6ZBo2dkcNU','education_3ank52Zi_S0','education_MnrJzXM7a6o','education_YtvP5A5OHpU','sports_NzYtFLpJrQU','movie_trailer_foyufD52aog','pet_ZkGTX3PUSHc','pet_z_AbfPXTKms','pet_LPjblqE3xHk','product_Mm0NvlXdz4A']:
                    import pdb; pdb.set_trace()
                """
    elif opt in ['3.000','3.001']:
        # watch out if removed seg...
        fids=None
        vv='product/enkRALcdPb0';fids=range(1525,1654)
        vv='product/JQk56_ZJEOo';fids=range(1525,1654)
        vv='tv/0oBodJHX1Vg';fids=range(1525,1654)
        vv='music_video/iS1g8G_njx8';
        vv = 'music_video/pRpeEdMmmQ0'
        vv = 'education/QOG6DAVFrkc'
        #vv = 'kid/J9IdcVG0Z-s'
        vv = 'cooking/noHAYjTjJKw'

        fns = sorted(glob(Dv + 'Annotations/' + vv.replace('/','_') + '/*.png'))
        ftemplate = os.path.dirname(fns[0])+'/%05d.png'
        ffs = np.array([int(x[x.rfind('/')+1 : x.rfind('.')]) for x in fns])
        fstep = (ffs[1:]-ffs[:-1]).min()
        fids = (np.arange(ffs[0],ffs[-1]+1,fstep)-1)/fstep

        if opt == '3.000':# pure copy for non-exist
            fids = (np.arange(ffs[0],ffs[-1]+1,fstep)-1)/fstep
            for fid in fids:
                fn = ftemplate % (fid*fstep+1)
                if not os.path.exists(fn):
                    nn = '%s/%s'% (vv[:vv.find('/')],vv[1+vv.find('/'):]) 
                    fn2 = 'db/share/%s/seg_prop_out/seg_%05d.png'%(nn,fid) 
                    fn3 = Dw + 'seg_ds/%s/r_seg_%05d.png'%(nn,fid*fstep+1) 
                    if os.path.exists(fn2):
                        print('copy',fn)
                        shutil.copy(fn2, fn)
                        if os.path.exists(fn3):
                            os.remove(fn3)
        elif opt == '3.001':# rewreit non-zero for the range
            for fid in fids:
                fn = ftemplate % (fid*fstep+1)
                if not os.path.exists(fn) or imread(fn).max()==0:
                    # re-copy from seg_prop_out
                    nn = '%s/%s'% (vv[:vv.find('/')],vv[1+vv.find('/'):]) 
                    fn2 = 'db/share/%s/seg_prop_out/seg_%05d.png'%(nn,fid) 
                    fn3 = Dw + 'seg_ds/%s/r_seg_%s.png'%(nn,fn[-9:-4]) 
                    if os.path.exists(fn2):
                        im2 = imread(fn2)
                        if im2.max()>0:
                            print(fn)
                            shutil.copy(fn2, fn)
                            if os.path.exists(fn3):
                                os.remove(fn3)
                if not os.path.exists(fn):
                    import pdb; pdb.set_trace()

    elif opt =='3.002':
        vvs = 'cooking/2c18PX9acwU'
        vv='cooking/_BcviWR9J1A'
        vv='music_video/YQHsXMglC9A'
        vv='sports/tG-IGNvfrg8'
        #fns = glob(Dw + 'seg_ds/' + vv + '/*.png')
        fns = glob(Dw + 'frame_ds/' + vv + '/*.png')
        for fn in fns:
            im = imread(fn)
            if im.shape[0] == 360:
                print(fn)
                imwrite(fn, im[::2,::2])
            """
            if im.max() == 0:
                print(fn)
                os.remove(fn)
            if im.shape[0] == 120:
                print(fn)
                os.remove(fn)
            """
            """
            if im.shape[0] == 180:
                imwrite(fn, im.transpose())
            """
    elif opt =='3.1': # remove small cc seg
        from skimage.measure import label
        fstep=5
        do_max = True;rl=[];topk=1
        #vv='product/N826TtJWxu4';sid=1;fstep=4;fids = range(1294,1321);do_max=False;rl=[0,2,1]
        #vv='tv/izh-j8KUYjs';sid=1;fstep=4;fids = range(1471,1523);topk=0
        #vv='education/QOG6DAVFrkc';sid=1;fstep=5;fids = range(515,537);do_max=False;rl=[0,2,2,2]
        vv='cooking/noHAYjTjJKw';sid=1;fstep=5;fids = list(range(723,735));do_max=False;rl=[0,1,1,1]
        #topk=1

        rl = np.array(rl).astype(np.uint8)
        for fid in fids:
            sn = Dw + 'seg_ds/' + vv + '/r_seg_%05d.png'%(1+fid*fstep)
            if os.path.exists(sn):
                os.remove(sn)
            sn = Dv + 'Annotations/' + vv.replace('/','_') + '/%05d.png'%(1+fid*fstep)
            seg = imread(sn)
            print(np.unique(seg))
            if np.any(seg==sid):
                if topk==0:
                    seg[seg==sid] = 0
                else:
                    if do_max:
                        out = label(seg==sid)
                        ui,uc = np.unique(out, return_counts=True)
                        uc[ui==0] = 0
                        print(fid,uc)
                        #import pdb; pdb.set_trace()
                        seg[seg==sid] = 0
                        if topk==1:
                            seg[out==ui[np.argmax(uc)]] = sid
                        else:
                            seg[np.in1d(out.reshape(-1),ui[np.argsort(-uc)[:topk]]).reshape(seg.shape)] = sid
                    else:
                        if len(rl) == 0:
                            seg[seg==sid] = 0
                        else:
                            seg = rl[seg]
                imwrite(sn, seg)
    elif opt =='3.11': # remove cc seg on the right
        from skimage.measure import label
        fstep=5;
        vv='sports/4rp2aLQl7vg';sid=4;fstep=5;fids = range(263,265);do_l=True
        vv='cooking/noHAYjTjJKw';sid=1;fstep=5;fids = list(range(846,859));do_l=False
        for fid in fids:
            sn = Dw + 'seg_ds/' + vv+ '/r_seg_%05d.png'%(1+fid*fstep)
            if os.path.exists(sn):
                os.remove(sn)
            sn = Dv + 'Annotations/' + vv.replace('/','_')  + '/%05d.png'%(1+fid*fstep)
            seg = imread(sn)
            if seg.max() > 0 and np.any(seg==sid):
                out = label(seg==sid)
                # keep top 2
                ui,uc = np.unique(out, return_counts=True)
                uc[ui==0]=0
                ii = np.argsort(-uc)
                b0 = vutil.get_bb(out==ii[0])
                b1 = vutil.get_bb(out==ii[1])
                gid = ii[0]
                if b0[2]<b1[2]: 
                    if not do_l:
                        gid = ii[1]
                else:
                    if do_l:
                        gid = ii[1]
                print(b0,b1,ii,gid)
                bid = ii[:2][np.in1d(ii[:2],gid,invert=True)][0]
                # keep 1 only 
                seg[seg==sid] = 0
                seg[out==gid] = sid
                #seg[out==bid] = 1

                imwrite(sn, seg)
    elif opt =='3.12': # copy seg
        fids = None
        """
        D0 = Dl2 + '/%05d.png'
        vv = 'pet/joEvL8gMVRM';fstep=5;fids = range(333,389)
        """

        vv = 'music_video/9bZkp7q19f0';fstep=4
        D0 = 'db/share/'+vv+'/gangnam_pf/_s%04d.png'
        if fids is None:
            fids = vutil.extractIdFolder(os.path.dirname(D0), shift=2)
        for fid in fids:
            fin = D0%(fid)
            fout = Dv + 'Annotations/' + vv.replace('/','_') + '/%05d.png'%(1+fid*fstep)
            shutil.copy(fin,fout)

    elif opt =='3.121': # copy seg
        fns = glob(Dv + 'Annotations/*_v1')
        for fn in fns:
            print(fn)
    elif opt == '3.122':# visualize frames
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
    elif opt =='3.13': # remove seg
        vv = 'education/P-QZ5Om9_20';fstep=5;sid=1;fids=range(64,70)
        for fid in fids:
            fin = Dv + 'Annotations/' + vv.replace('/','_') + '/%05d.png'%(1+fid*fstep)
            seg = imread(fin)
            if np.any(seg==sid):
                print(fid)
                seg[seg==sid] = 0
                imwrite(fin, seg)
                sn = Dw + 'seg_ds/' + vv + '/r_seg_%05d.png'%(1+fid*fstep)
                if os.path.exists(sn):
                    os.remove(sn)
    elif opt =='3.14': # fill seg
        from scipy.ndimage import binary_fill_holes
        vv = 'howto_T0NPYZyI7V8';fstep=4;sid=1;fids=[721]
        vv = 'music_video_iS1g8G_njx8';fstep=4;sid=3;fids=[1055]
        for fid in fids:
            fin = Dv + 'Annotations/' + vv + '/%05d.png'%(1+fid*fstep)
            seg = imread(fin)
            if np.any(seg==sid):
                print(fid)
                seg[binary_fill_holes(seg==sid)] = sid
                imwrite(fin, seg)
                sn = Dw + 'seg_ds/' + vv.replace('_','/') + '/r_seg_%05d.png'%(1+fid*fstep)
                if os.path.exists(sn):
                    os.remove(sn)
    elif opt =='3.15': # relabel seg
        vv = 'howto/qsxcVsFDDoA';fstep=5;fids=range(3954,4089);rl=np.ones([10])*2;
        vv = 'product/JQk56_ZJEOo';fstep=4;fids=range(421,427);rl=np.ones([10])*3;
        vv = 'tv/qVMW_1aZXRk';fstep=5;fids=range(1100,1164);rl=np.ones([10])*4;
        vv = 'tv/_yl2fV6SM_8';fstep=5;fids=range(1767,1774);rl=np.ones([10])*4;
        rl=rl.astype(np.uint8)
        rl[0]=0
        for fid in fids:
            fin = Dv + 'Annotations/' + vv.replace('/','_') + '/%05d.png'%(1+fid*fstep)
            seg = imread(fin)
            imwrite(fin, rl[seg])
            sn = Dw + 'seg_ds/' + vv + '/r_seg_%05d.png'%(1+fid*fstep)
            if os.path.exists(sn):
                os.remove(sn)
    elif opt =='3.16': # fill seg
        vv = 'education/P-QZ5Om9_20';fstep=5;fids=range(29,40);sid=1
        for fid in fids:
            fin = Dv + 'Annotations/' + vv.replace('/','_') + '/%05d.png'%(1+fid*fstep)
            seg = imread(fin)
            seg[:] = sid
            imwrite(fin, seg)
            sn = Dw + 'seg_ds/' + vv + '/r_seg_%05d.png'%(1+fid*fstep)
            if os.path.exists(sn):
                os.remove(sn)
    elif opt == '3.2': # remove bbox
        from skimage.measure import label
        from scipy.ndimage import binary_fill_holes
        D0 = '/n/boslfs02/LABS/lichtman_lab/donglai/youtop/education/'

        # faster to do manual bbox..
        vv='education/1NIhv6fCqAU'
        fids = range(69,1443)
        bb = [625, 668, 213, 1074]
        fids = list(range(179,204))+list(range(1035,1059))
        bb[0] = 550

        vv='howto/nEQQle9-0NA'
        bb = [574, 674, 0, 1280]
        fids = list(range(116,174)) + list(range(1135,1209)) + list(range(1478,1622)) + list(range(1763,1798)) + list(range(2231,2312)) + list(range(2326,2379))

        """
        imN = D0 + 'image_00601.png'
        im = imread(imN)
        imG = im[:,:,1]
        imG[im[:,:,0]>200] = 0
        imG[im[:,:,2]>200] = 0
        thres = np.percentile(imG[:], 80)
        mask = imG >thres 
        mask[:600] = 0
        mask_l = label(mask)
        ui,uc = np.unique(mask_l, return_counts=True)
        uc[ui==0] = 0
        out = binary_fill_holes(mask_l == ui[np.argmax(uc)])
        #imwrite(D0+'mask.png', out.astype(np.uint8))
        rsum = out.sum(axis=1)
        csum = out.sum(axis=0)
        rr = np.where(rsum>rsum.max()*0.1)[0]
        cc = np.where(csum>csum.max()*0.1)[0]
        bb = [rr[0], rr[-1]+1, cc[0], cc[-1]+1]
        """

        #im[bb[0]:bb[1],bb[2]:bb[3]] = 0
        #imwrite(D0+'out.png', im)
        D2 = '/n/pfister_lab2/Lab/vcg_natural/YouTop200/release/Annotations/'+vv.replace('/','_')+'/%05d.png'
        for fid in fids:
            fn = D2%(fid*5+1)
            im = imread(fn)
            im[bb[0]:bb[1],bb[2]:bb[3]] = 0
            imwrite(fn, im)
            fn3 = Dw + 'seg_ds/%s/r_seg_%05d.png'%(vv,fid*5+1) 
            if os.path.exists(fn3):
                os.remove(fn3)
    elif opt == '3.21':
        D2 = '/n/pfister_lab2/Lab/vcg_natural/YouTop200/release/Annotations/education_1NIhv6fCqAU/%05d.png'
        fids = list(range(977,1015)) + list(range(941,967)) + list(range(906,930)) + list(range(882,897)) + list(range(407,446)) + list(range(374,394)) + list(range(218,224)) + list(range(136,153))
        bb = [672,720,652,882] 
        for fid in fids:
            fn = D2%(fid*5+1)
            im = imread(fn)
            if im.max()!=3:
                import pdb; pdb.set_trace()
            im[bb[0]:bb[1],bb[2]:bb[3]] = 3
            imwrite(fn, im)
            fn3 = Dw + 'seg_ds/education/1NIhv6fCqAU/r_seg_%05d.png'%(fid*5+1) 
            if os.path.exists(fn3):
                os.remove(fn3)
    elif opt == '3.22':#mask out
        vv = 'cooking/u6TFP_r2oA8';fstep=4;mid = 0
        mn='1';fids = range(179,188)
        #mn='2';fids = range(856,873)
        #mn='3';fids = range(1262,1273)

        vv = 'tv/0oBodJHX1Vg';fstep=5;mid = 2
        mn='1';fids = np.hstack([range(220,236)])#np.hstack([range(34,148), range(164,199), range(258,398)])

        mask = imread('/n/boslfs02/LABS/lichtman_lab/donglai/youtop/%s/logo%s.png'%(vv,mn))
        D2 = '/n/pfister_lab2/Lab/vcg_natural/YouTop200/release/Annotations/'+vv.replace('/','_')+'/%05d.png'
        for fid in fids:
            fn = D2%(fid*fstep+1)
            im = imread(fn)
            im[mask>0] = mid
            imwrite(fn, im)
            fn3 = Dw + 'seg_ds/%s/r_seg_%05d.png'%(vv,fid*fstep+1) 
            if os.path.exists(fn3):
                os.remove(fn3)

    elif opt == '3.3':# copy 1fps to folder
        vv = 'tv/qVMW_1aZXRk';fstep=5

        nn = '%s/%s'% (vv[:vv.find('/')],vv[1+vv.find('/'):]) 
        fin = 'db/share/%s/seg_prop_out/'%nn
        fmax = vutil.extractIdFile(sorted(glob(fin + '/*.png'))[-1])
        fin += 'seg_%05d.png'
        fout = Dl2+ '%s/seg_prop_1fps/'%nn +'%05d.png'
        vutil.mkdir(fout, 'parent')
        for i,fid in enumerate(range(0,fmax+1,fstep)):
            if i<=30:
                continue
            fn = fin % fid
            if os.path.exists(fn):
                shutil.copy(fn, fout%i)
    elif opt == '3.31':# copy Annotations
        vv = 'tv/_yl2fV6SM_8';fstep=5
        fin=range(250,262);fout=range(3164,3179)
        fin=range(250,262);fout=range(3164,3179)

elif opt[0] == '4':
    if opt == '4':# debug: why miss every K seg
        vv = 'pet/YChHbz5VVoM'
        # seg_prop.txt: 1 FPS
        # seg_prop_out.txt: 6 FPS
        # run_stm3.sh
        # debug STM
        seg = imread('db/share/%s/seg_prop_out/seg_00004.png'%vv)
        seg2 = imread(Dv+'Annotations/%s/00021.png'%vv.replace('/','_'))
        print(seg.max())
        import pdb; pdb.set_trace()
    elif opt == '4.1': # rename detectron2
        arr = [485,677,701,901,913,1145,1161,1181,1253,1397,1413,1445,2141,2285,2433,2685,2789,3485,3509,3729,3989,4061,4157,4257,4289,4349,4473,41,45,437,605,609,613,617,621,789,801,805,825,821,813,809,1281,1277,1361,1365,1373,1377,1381,1393,1389,1385,1505,1509,1533,1529,1545,1549,1557,1553,1565,1569,1741,1737,2613,2705,2721,2717,2981,3013,3445,3541,3605,3609,3589,3593,3645,3641,3773,3777,3781,3785,3789,3809,3801,3797,3805,3913,3909,4029,4041,4045,4173,4181,4185,4189,4253,4485,5053,5225,5405,5421,5417,5409,5413]
        fn = '/n/boslfs02/LABS/lichtman_lab/donglai/tmp/seg_%05d.png'
        for i,x in enumerate(arr):
            shutil.move(fn%x, fn%i)
    elif opt =='4.11':
        arr = [1357,1358,1359,1360,1361,1363,1364,1365,1366,1367,1369,1370,1371,1372,1373,1375,1376,1377,1378,1379,1381,1382,1383,1384,1385,1466,1467,1468,1469,1471,1472,1473,1474,1475,1477,1478,1479,1480,1481,1483,1484,1485,1533,1534,1535,1537,1538,1539,1540,1541,1543,1544,1545,1546,1547,1597,1598,1599,1600,1601,1603,1604,1605,1606,1633,1634,1635,1636,1637,1639,1640,1641,1642,1666,1667,1681,1682,1683,1684,1685,1687,1688,1689,1690,1691,1693,1694,1695,1696,1697,1699,1700,1701,1702,1703,1705,1706,1707,1708,1709,1711,1712,1713,1714,1715,1717,1718,1719,1720,1721,1723,1724,1725,1726,1727,1729,1730,1731,1732,1733,1735,1736,1737,1738,1739,1741,1742,1743,1744,1745,1747,1748,1749,1750,1751,1753,1754,1755,1756]
        for i in arr:
            os.remove('db/share/pet/YChHbz5VVoM/seg_prop_out/seg_%05d.png'%i)

    elif opt in ['4.2','4.21']:# STM index
        # ls scripts/;python scripts/T_refactor.py 4.21
        # ls scripts/;python scripts/T_refactor.py 3.001
        # ls;python main.py web-proofread-seg-release@pet/QlYUH5mARF0 -v data/video_rest.txt
        input_image = ''
        input_mask = ''
        output_image = ''
        output_mask = ''
        if opt == '4.2':#use existing anchor
            vv = 'pet/YChHbz5VVoM';fstep=5;
            ind = '1356-1385,1466-1485,1533-1547,1597-1606,1633-1642,1666-1668,1681-1756'
            ind_g = vutil.extractIdFolder(os.path.dirname(mt))
            ind2 = str2Arr(ind, arr=False)
            ind1 = [None]*len(ind2)
            for i,j in enumerate(ind2):
                ind1[i] = vutil.removeArr(ind_g, j, False)
        elif opt == '4.21':
            vv = 'pet/1PmJbBG_0JM';fstep=4;
            ind1 = [[480],[480],[492],range(492,517,6)]
            ind2 = [range(475,480),range(481,486),range(488,492),range(492,518)]
            vv = 'pet/8GwmRn0_Y-Y';fstep=4;
            ind1 = [range(1200,1225,6),range(1272,1303,6)]
            ind2 = [range(1191,1231),range(1259,1309)]

            vv = 'pet/QlYUH5mARF0';fstep=5;
            ind1 = [[426],range(582,619,6),range(636,661,6),range(678,685,6),range(696,715),range(852,907,6)]
            ind2 = [range(427,430),range(579,620),range(632,665),range(673,689),range(694,720),range(847,909)]

            vv = 'product/enkRALcdPb0';fstep=5;
            ind1 = [range(1530,1651,6)]
            ind2 = [range(1526,1654)]

            vv = 'product/9GysUQfI3ZQ';fstep=4;# todo
            ind1 = [[1332],[1368],[1314],[1272]]
            ind2 = [range(1333,1341),range(1367,1361,-1),range(1315,1320),range(1273,1284)]

            vv = 'product/JQk56_ZJEOo';fstep=4;
            ind1 = [[207],[53],[142],[116],[110],[261]]
            ind2 = [[208],range(73,77),range(77,89),range(107,93,-1),range(89,94),range(245,240,-1)]
        
            vv = 'tv/qVMW_1aZXRk';fstep=5;
            ind1 = [[55],[907]]
            ind2 = [np.hstack([range(56,237),range(365,382),range(525,640),range(2363,2446),range(2529,2580),range(2599,2647)]), np.hstack([range(908,938),range(953,969),range(2207,2226),range(2842,2868)])]
            vv = 'product/JQk56_ZJEOo';fstep=4;
            ind1 = [[3290]]
            ind2 = [range(3289,3267,-1)]

            vv = 'music_video/iS1g8G_njx8';fstep=4;
            #ind1 = [[145],[391],[534],[932],[963],[571],[573],[587],[911],[932],[932],[1037],[1105]]
            #ind2 = [range(151,153),range(379,384),range(517,521),np.hstack([range(937,940),range(943,946)]),range(950,953),range(614,618),range(577,582),range(610,612),range(915,918),range(937,940),np.hstack([range(943,946),range(950,953)]),range(548,551),range(1101,1104)]
            ind1 = [[146],[183],[216],[310],[642],[580],[1081],[615]]
            ind2 = [range(143,139,-1),[509],range(223,228),range(305,302,-1),range(628,625,-1),[579,578],np.hstack([range(591,588,-1),range(583,581,-1)]),[1005]]

            vv = 'kid/J9IdcVG0Z-s';fstep=5;
            ind1 = [[24],[36],[48],[60],[60],[90],[126],[162],[228],[264],[336],[402],[414],range(468,487,6),[516],[522],[630],[642],[708],[774],[882],[888],[1008],[1032]]
            ind2 = [[25],range(37,41),np.hstack([range(46,48),range(49,54)]),range(59,57,-1),range(61,66),[117],[125,129,130,133,134,137,138,141,142,144,145,146],[163,164],np.hstack([range(227,224,-1),range(229,256)]),np.hstack([range(263,259,-1),range(265,276)]),np.hstack([range(335,324,-1),range(337,348)]),np.hstack([range(401,398,-1),range(403,409)]),np.hstack([range(413,409,-1),range(415,423)]),range(467,491),np.hstack([range(515,512,-1),range(517,521)]),range(523,528),range(631,633),np.hstack([range(641,639,-1),range(643,649)]),np.hstack([range(707,705,-1),range(709,713)]),range(775,783),range(881,879,-1),np.hstack([range(887,886,-1),range(889,924)]),np.hstack([range(1007,1005,-1),range(1009,1028)]),np.hstack([range(1031,1027,-1),range(1033,1063)])]

            vv = 'music_video/pRpeEdMmmQ0';fstep=4;
            ind1 = [[1026]]
            ind2 = [range(1025,1020,-1)]

            vv = 'tv/izh-j8KUYjs';fstep=4;
            ind1 = [range(36,61,6),range(252,289,6),[621]]
            ind2 = [range(33,63),range(249,293),range(597,615)]

            vv='education/QOG6DAVFrkc';fstep=5;
            ind2 = [[2484],[2773],[2915],[2921]]
            ind1 = [range(2483,2469,-1),[2772],[2916,2914,2913,2912],[2922]]
        mt='db/share/%s/'%vv+'seg_prop_out/seg_%05d.png'
        ind2 = [vutil.removeArr(x,y) for x,y in zip(ind2,ind1)]
        for i,j in zip(ind1,ind2):
            ii = np.array(i)
            jj = np.array(j)
            num2 = len(ii) - 1 + (ii[0]>jj.min()) + (ii[-1]<jj.max())
            tmp_im = [None]*num2
            tmp_om = [None]*num2
            st = 0
            if ii[0]>jj.min():
                tmp_im[0] = [ii[0]]
                tmp_om[0] = jj[jj<ii[0]]
                st = 1
            if ii[-1]<jj.max():
                tmp_im[-1] = [ii[-1]]
                tmp_om[-1] = jj[jj>ii[-1]]
            for x in range(len(ii)-1):
                tmp_im[st + x] = ii[x:x+2]
                tmp_om[st + x] = jj[(jj>ii[x])*(jj<ii[x+1])]
            tmp_im = [x for x,y in zip(tmp_im,tmp_om) if len(y)>0]
            tmp_om = [x for x in tmp_om if len(x)>0]
            tmp_ii = [np.array(x) * fstep + 1 for x in tmp_im]
            tmp_oi = [np.array(x) * fstep + 1 for x in tmp_om]
            input_image += vutil.convertClusterListToStr(tmp_ii)
            output_image += vutil.convertClusterListToStr(tmp_oi)
            input_mask += vutil.convertClusterListToStr(tmp_im)
            output_mask += vutil.convertClusterListToStr(tmp_om)
            for k in np.hstack(tmp_oi):
                fn = Dv + 'Annotations/%s/%05d.png' % (vv.replace('/','_'),k)
                if os.path.exists(fn):
                    os.remove(fn)
            """
            ind1_f = [np.array(x)*fstep+1 for x in ind1]
            ind2_f = [np.array(x)*fstep+1 for x in ind2]
            input_image = vutil.convertClusterListToStr(ind1_f)
            output_image = vutil.convertClusterListToStr(ind2_f)
            input_mask = vutil.convertClusterListToStr(ind1)
            output_mask = vutil.convertClusterListToStr(ind2)
            """
        cmd = 'python /n/pfister_lab2/Lab/donglai/lib/pipeline/STM/demo_youtop.py --image-template %s --image-input-index "%s" --image-output-index "%s" --mask-template-input %s --mask-input-index "%s" --mask-template-output %s --mask-output-index "%s" --stm-height 480 --stm-mem-step 1 --stm-mem-len 100 --redo 1\n'
        it='/n/pfister_lab2/Lab/vcg_natural/YouTop200/'+vv+'/frame/image_%05d.png'
        print(cmd %(it, input_image,output_image,mt,input_mask,mt,output_mask))

elif opt[0] == '5':# all 200 videos
    if opt == '5': # 3.001 bug: copy prop_out to final
        vvs = vutil.readtxt('data/cvpr2022_final.txt')
        for vv in vvs[176:]:
            gn,vn = vv[:-13],vv[-12:-1]
            Din = 'db/share/%s/%s/seg_prop_out/'%(gn,vn)
            Do = Dv+'Annotations/%s/'%(vv[:-1])
            print(Din)
            if os.path.exists(Din):
                fns = glob(Din + '*.png')
                for fn in fns: 
                    fn2 = Do + fn[fn.rfind('_')+1:]
                    if os.path.exists(fn2):
                        im = imread(fn)
                        if im.max()>0:
                            im2 = imread(fn2).astype(float)
                            try:
                                if np.abs(im2-im).max()==0:
                                    print('error!')
                                    import pdb; pdb.set_trace()
                            except:
                                import pdb; pdb.set_trace()
    elif opt == '5.1': # 3.001 bug: copy prop_out to final
        fn = 'db/demo/cvpr2022_demo'
        #fn = 'data/cvpr2022_final'
        vvs = vutil.readtxt(fn+'.txt')
        for i in range(len(vvs)):
            gn,vn = vvs[i][:-13],vvs[i][-12:-1]
            vvs[i] = gn+'/'+vn
        vutil.writetxt(fn + '2.txt',vvs)
    elif opt == '5.11': # 3.001 bug: copy prop_out to final
        job_id = int(sys.argv[2])
        job_num = int(sys.argv[3])
        vvs = [x.replace('\n','') for x in vutil.readtxt('db/demo/cvpr2022_demo2.txt')]
        for vv in vvs:
            vv2 = vv.replace('/','_')
            Dim = Dv+'JPEGImages/%s/'%(vv2)+'/%05d.jpg'
            Dseg = Dv+'Annotations/%s/'%(vv2)+'/%05d.png'
            Do = 'db/demo/%s/'%vv2+'/%05d.png'
            vutil.mkdir(Do, 'parent')
            info = json.load(open('db/demo/cvpr2022_demo2.json'))
            frame_step = getFrameStep(info[vv]['fps'])
            frame_len = int(info[vv]['num_frame'])
            ind = [x+1 for x in range(job_id*frame_step,frame_len,job_num*frame_step)]
            for ii in ind:
                if not os.path.exists(Do%ii):
                    im = imread(Dim % ii)
                    seg = imread(Dseg % ii)
                    im = vutil.visSeg(im,seg)
                    imwrite(Do % (ii-1)//frame_step, im)
    elif opt == '5.12': # 3.001 bug: copy prop_out to final
        vvs = [x.replace('\n','') for x in vutil.readtxt('db/demo/cvpr2022_demo2.txt')]
        for vv in vvs:
            vv2 = vv.replace('/','_')
            Dim = Dv+'JPEGImages/%s/'%(vv2)+'/%05d.jpg'
            Dseg = Dv+'Annotations/%s/'%(vv2)+'/%05d.png'
            Do = 'db/demo/%s/'%vv2+'/%05d.png'
            vutil.mkdir(Do, 'parent')
            info = json.load(open('db/demo/cvpr2022_demo2.json'))
            frame_step = getFrameStep(info[vv]['fps'])
            frame_len = int(info[vv]['num_frame'])
            ind = [x+1 for x in range(job_id*frame_step,frame_len,job_num*frame_step)]
            for ii in ind:
                if not os.path.exists(Do%ii):
                    im = imread(Dim % ii)
                    seg = imread(Dseg % ii)
                    im = vutil.visSeg(im,seg)
                    imwrite(Do % (ii-1)//frame_step, im)
                    
    elif opt == '5.12': # 3.001 bug: copy prop_out to final
        D0='db/demo/music_video_9bZkp7q19f0/'
        fns = sorted(glob(D0 + '*.png'))
        for fid,fn in enumerate(fns):
            shutil.move(fn,D0+'%05d.png'%fid)
    elif opt == '5.13': # 3.001 bug: copy prop_out to final
        vvs = [x.replace('\n','') for x in vutil.readtxt('db/demo/cvpr2022_demo2.txt')]
        info = json.load(open('db/demo/cvpr2022_demo2.json'))
        for vv in vvs:
            vv2 = vv.replace('/','_')
            Do = 'db/demo/%s'%vv2
            fps = int(np.round(info[vv]['fps']))
            frame_step = getFrameStep(info[vv]['fps'])
            cmd='ffmpeg -f image2 -framerate {} -i {}/%05d.png -c:v libx264 -preset veryslow -crf 18 -pix_fmt yuv420p {}.mp4'.format(fps//frame_step,Do,Do)
            print(cmd)

    elif opt == '5.2': # 3.001 bug: copy prop_out to final
        vvs = vutil.readtxt('data/cvpr2022_final.txt')
        for vv in vvs:
            print('https://www.youtube.com/watch?v='+vv[-12:-1])
elif opt == '-1':# debug
    """
    D0 = '/n/pfister_lab2/Lab/donglai/YouTop200/db/share/kid/J9IdcVG0Z-s/'
    ind = [1,61,3301,3781,3961,4261,4411,3811,3871,4441,4831,4861,5041,5161,5341,121,151,181,301,451,361,631,661,271,3211,1291,1321,241,811,901,1141,1681,2131,841,2491,1771,2011,2071,2611,2671,2701,2581,3181,3271,3541,3601]
    fin = D0 + 'seg_shot_bd/_s%02d.png'
    fout = D0 + 'seg_prop_out/seg_%05d.png'
    for i in range(len(ind)):
        shutil.copy(fin%i, fout%((ind[i]-1)//5))
    """
    D0 = '/n/boslfs02/LABS/lichtman_lab/donglai/youtop/tv/qVMW_1aZXRk/seg_prop_1fps/'
    for i in range(61):
        shutil.move(D0+'_s%03d.png'%i,D0+'%05d.png'%i)

elif opt == '-2':# debug
    vv = 'tv/qVMW_1aZXR';sids = [55,907]
    vv = 'tv/_yl2fV6SM_8';sids=[3320]
    vv = 'tv/izh-j8KUYjs';sids=[600,606]
    vv = 'education/QOG6DAVFrkc';sids=[1057];fstep=5
    vv = 'kid/epADzQLGE0w';sids=[138];fstep=4
    fn='/n/pfister_lab2/Lab/vcg_natural/YouTop200/release/Annotations/%s/%05d.png'
    fn2 ='db/share/%s/seg_prop_out/seg_%05d.png'
    for sid in sids:
        print(np.unique(imread(fn2%(vv,sid))))
        print(np.unique(imread(fn%(vv,sid*fstep+1))))
elif opt == '-2.1':# debug
    def getVV(fn, opt=0):
        if opt == 0:
            return [x.replace('\n','') for x in vutil.readtxt(fn)]
        elif opt == 1:
            return [x.replace('\n','').replace('/','_') for x in vutil.readtxt(fn)]
    """
    v0 = getVV('data/cvpr2022_final.txt') 
    vr = getVV('data/video_rest.txt',1)
    vv = getVV('data/video_done_f.txt',1)
    vv2 = getVV('data/video_done.txt',1)
    #dd = [x for x in vr if x in vv2]
    #dd = [x for x in v0 if x not in vv2 and x not in vr]
    dd = [x for x in vv2 if x not in vv]
    # print(len(vv), len(vv2), len(dd))
    import pdb; pdb.set_trace()
    """
    v0 = getVV('data/cvpr2022_final.txt') 
    vv = []
    for nn in ['train','val','test']:
        vv = vv + getVV(Dv+'info/cvpr2022_%s.txt'%nn) 
    dd = [x for x in v0 if x in vv]
    import pdb; pdb.set_trace()
elif opt == '-3':# release
    v0 = [x[:-1] for x in vutil.readtxt('data/video_done_f.txt')]
    fns = glob(Dl2 + '*') 
    out = []
    for fn in fns:
       #print(fn)
       fn2 = fn[fn.rfind('/')+1:]
       gns = glob(fn + '/*.zip')
       for gn in gns:
           if 'segr3_' not in gn:
               gn2 = fn2+'/'+gn[gn.rfind('/')+1:-7]
               #print(gn2)
               out.append(gn2)
               # check file number
               num1 = len(glob(gn[:-4] + '/*.png'))
               num2 = len(glob(Dv + 'JPEGImages/%s/'%(gn2.replace('/','_')) + '/*.jpg'))
               if num1 != num2:
                   # some only save nonzero frame
                   # movie_trailer/9382rwoMiRc
                   print(gn,num1,num2)
                   import pdb; pdb.set_trace()
               #os.system('unzip -r %s'%gn)
    import pdb; pdb.set_trace()
    #dif = [x for x in v0 if x not in out]
elif opt == '-4':# zip cmd
    aa = [x[:x.find(',')] for x in vutil.readtxt('db/round3/sid.txt')]
    for a in aa:
        print(a)
        D0='db/demo/music_video_9bZkp7q19f0/'
        fns = sorted(glob(D0 + '*.png'))
        for fid,fn in enumerate(fns):
            shutil.move(fn,D0+'%05d.png'%fid)
elif opt == '-1':# debug
    """
    D0 = '/n/pfister_lab2/Lab/donglai/YouTop200/db/share/kid/J9IdcVG0Z-s/'
    ind = [1,61,3301,3781,3961,4261,4411,3811,3871,4441,4831,4861,5041,5161,5341,121,151,181,301,451,361,631,661,271,3211,1291,1321,241,811,901,1141,1681,2131,841,2491,1771,2011,2071,2611,2671,2701,2581,3181,3271,3541,3601]
    fin = D0 + 'seg_shot_bd/_s%02d.png'
    fout = D0 + 'seg_prop_out/seg_%05d.png'
    for i in range(len(ind)):
        shutil.copy(fin%i, fout%((ind[i]-1)//5))
    """
    """
    D0 = '/n/boslfs02/LABS/lichtman_lab/donglai/youtop/tv/qVMW_1aZXRk/seg_prop_1fps/'
    for i in range(61):
        shutil.move(D0+'_s%03d.png'%i,D0+'%05d.png'%i)

    """
elif opt == '-2':# debug
    vv = 'tv/qVMW_1aZXR';sids = [55,907]
    vv = 'tv/_yl2fV6SM_8';sids=[3320]
    vv = 'tv/izh-j8KUYjs';sids=[600,606]
    vv = 'education/QOG6DAVFrkc';sids=[1057];fstep=5
    vv = 'kid/epADzQLGE0w';sids=[138];fstep=4
    fn='/n/pfister_lab2/Lab/vcg_natural/YouTop200/release/Annotations/%s/%05d.png'
    fn2 ='db/share/%s/seg_prop_out/seg_%05d.png'
    for sid in sids:
        print(np.unique(imread(fn2%(vv,sid))))
        print(np.unique(imread(fn%(vv,sid*fstep+1))))
elif opt == '-2.1':# debug
    def getVV(fn, opt=0):
        if opt == 0:
            return [x.replace('\n','') for x in vutil.readtxt(fn)]
        elif opt == 1:
            return [x.replace('\n','').replace('/','_') for x in vutil.readtxt(fn)]
    """
    v0 = getVV('data/cvpr2022_final.txt') 
    vr = getVV('data/video_rest.txt',1)
    vv = getVV('data/video_done_f.txt',1)
    vv2 = getVV('data/video_done.txt',1)
    #dd = [x for x in vr if x in vv2]
    #dd = [x for x in v0 if x not in vv2 and x not in vr]
    dd = [x for x in vv2 if x not in vv]
    # print(len(vv), len(vv2), len(dd))
    import pdb; pdb.set_trace()
    """
    v0 = getVV('data/cvpr2022_final.txt') 
    vv = []
    for nn in ['train','val','test']:
        vv = vv + getVV(Dv+'info/cvpr2022_%s.txt'%nn) 
    dd = [x for x in v0 if x in vv]
    import pdb; pdb.set_trace()
elif opt == '-3':# release
    v0 = [x[:-1] for x in vutil.readtxt('data/video_done_f.txt')]
    fns = glob(Dl2 + '*') 
    out = []
    for fn in fns:
       #print(fn)
       fn2 = fn[fn.rfind('/')+1:]
       gns = glob(fn + '/*.zip')
       for gn in gns:
           if 'segr3_' not in gn:
               gn2 = fn2+'/'+gn[gn.rfind('/')+1:-7]
               #print(gn2)
               out.append(gn2)
               # check file number
               num1 = len(glob(gn[:-4] + '/*.png'))
               num2 = len(glob(Dv + 'JPEGImages/%s/'%(gn2.replace('/','_')) + '/*.jpg'))
               if num1 != num2:
                   # some only save nonzero frame
                   # movie_trailer/9382rwoMiRc
                   print(gn,num1,num2)
                   import pdb; pdb.set_trace()
               #os.system('unzip -r %s'%gn)
    import pdb; pdb.set_trace()
    #dif = [x for x in v0 if x not in out]
elif opt == '-4':# zip cmd
    aa = [x[:x.find(',')] for x in vutil.readtxt('db/round3/sid.txt')]
    for a in aa:
        print(a)
