import sys,os
import numpy as np
# sa vis

opt = sys.argv[1]

Dv = '/n/pfister_lab2/Lab/vcg_natural/YouTop200/'
Dvr = Dv + 'release/'
Ds='/n/pfister_lab2/Lab/donglai/YouTop200/db/share/{}/seg_prop_out/seg_%05d.png'
Di=Dv+'{}/frame/image_%05d.png'
Dw='/n/boslfs02/LABS/lichtman_lab/glichtman/public/vcg/youtop-vis/youtube/'

if opt[0] == '0':
    from vidtool import videoTool
    vtool = videoTool()
    vtool.data.setInputVideoJson('data/video.json')
    video_names = vtool.data.video_all_name

    vvs = vtool.util.readtxt('db/v2.txt')
    vvs = [x[:-1] for x in vvs]
    if opt == '0':
        import shutil
        for vv in vvs:
            fn = Dvr + 'Annotations/' + vv.replace('/','_') + '/'
            fn2 = Dvr + 'Annotations/' + vv.replace('/','_') + '_v1/'
            """
            shutil.move(fn ,fn2)
            os.mkdir(fn)
            shutil.copy(fn2 + 'shot.txt', fn + 'shot.txt')
            """
            if os.path.exists(fn2 + 'no_eval.txt'):
                shutil.copy(fn2 + 'no_eval.txt', fn + 'no_eval.txt')
            print(fn)
    elif opt == '0.1':
        print(sorted([x[x.find('/'):] for x in vvs]))
        #print(sorted(vvs))
    elif opt == '0.2':
        from glob import glob
        import imageio
        from vidtool.lib import segRefinement
        job_id = int(sys.argv[2])
        job_num = int(sys.argv[3])

        seg_rf = segRefinement() 
        Do = 'db/v2_pf/'
        # for i in *.zip;do unzip ${i};done
        # manually adjust the folder name xx_pf
        # put back into folders
        """
        genre = [x[:-1]+'/' for x in vtool.util.readtxt('data/video_genre.txt')]
        for g in genre:
            vtool.util.mkdir(Do + g)
        """
        D1 = Dvr+'JPEGImages/'
        for vv in vvs[job_id::job_num]:
            # print(Do + vv[vv.rfind('/')+1:], Do+vv.replace('/','_'))
            vv_seg = vv[vv.rfind('/')+1:]
            vv_im = vv.replace('/','_')
            D2 = Dvr+'Annotations/' + vv_im + '/'
            if False:
                # check number of image and seg
                num1 = len(glob(D1 + vv_im + '/*.jpg'))
                num2 = len(glob(Do + vv_seg + '/*.png'))
                if num1!=num2:
                    print(vv,num1,num2)

            num1 = len(glob(D1 + vv_im + '/*.jpg'))
            num_seg = len(glob(Do + vv_seg + '_pf/*.png'))
            num2 = len(glob(D2 + '/*.png'))
            if num1 == num2:
                continue
            else:
                print(vv,num1,num2,num_seg)
                #import pdb; pdb.set_trace()
            
            fn_im = sorted(glob(D1 + vv_im + '/*.jpg'))
            fn_seg = sorted(glob(Do + vv_seg + '_pf/*.png'))
            fn_seg_pref = fn_seg[0][fn_seg[0].rfind('/'):]
            fn_seg_id = [x for x in range(len(fn_seg_pref)) if fn_seg_pref[x].isdigit()]
            fn_seg_pref = fn_seg[0][:fn_seg[0].rfind('/')] + fn_seg_pref[:fn_seg_id[0]]+'%0'+str(len(str(len(fn_im))))+'d.png'
            black = imageio.imread(fn_seg[0])
            black[:] = 0
            for i in range(len(fn_im)):
                output_name = fn_im[i][:-3].replace('JPEGImages','Annotations') + 'png' 
                if not os.path.exists(output_name):
                    if i % 10 == 0:
                        print(vv,i,len(fn_im))
                    im = imageio.imread(fn_im[i])
                    if os.path.exists(fn_seg_pref % i):
                        seg = imageio.imread(fn_seg_pref % i)
                        if seg.max()>0:
                            seg_out = seg_rf.segRefineGrabcut(im, seg)
                            imageio.imwrite(output_name, seg_out)
                        else:
                            imageio.imwrite(output_name, seg)
                    else:
                        imageio.imwrite(output_name, black)
    elif opt == '0.3': # vast for gangnum
        from glob import glob
        import shutil
        # grabcut result
        ims = sorted(glob(Dvr + 'Annotations/music_video_9bZkp7q19f0/*.png'))
        Do = '/n/boslfs02/LABS/lichtman_lab/donglai/tmp/%05d.png'
        for i in range(len(ims)):
            shutil.copy(ims[i], Do%i)
    elif opt == '0.31': # vast for gangnum
        from glob import glob
        import cv2
        # median filter
        #ims = sorted(glob(Dvr + 'Annotations/music_video_9bZkp7q19f0_v1/*.png'))
        # Tanav v2
        ims = sorted(glob('db/v2_pf/9bZkp7q19f0_pf/*.png'))
        Do = '/n/boslfs02/LABS/lichtman_lab/donglai/tmp2/%05d.png'
        for i in range(len(ims)):
            out = cv2.imread(ims[i], cv2.IMREAD_GRAYSCALE)
            if out.max() != 0:
                out = out * cv2.medianBlur((out>0).astype(np.uint8), 5)
            cv2.imwrite(Do%i, out)

elif opt[0] == '1': # youtube-vis visualization
    import json
    Dv = '/n/pfister_lab2/Lab/vcg_natural/YouTube-VIS/' 
    Da = 'db/ytvis_sid/'
    Dw = '/n/pfister_lab2/Lab/public/YouTube-VIS/sid_20211113/' 
    jj= json.load(open(Dv + 'vis/valid.json'))
    if opt == '1': # gt
        import cv2
        import mmcv
        import pycocotools.mask as maskUtils

        result = mmcv.load(Da + 'htc_YTVis_001.pkl')
        vv = jj['videos']
        num = 5
        # 360p
        rid = 0
        for i in range(len(vv)):
            fn = vv[i]['file_names']
            fid = np.linspace(0, len(fn)-1, num).astype(int)
            for f in range(num):
                Do = Dw + '%d/%d.png'
                ff = fid[f]
                resf = result[rid + ff]
                im = cv2.imread(Dv + 'valid/JPEGImages/' + fn[ff])
                if resf[0] == {}:
                    cv2.imwrite(Do%(i,f), im[::2,::2])
                else:
                    obj_ids = resf[1].keys()
                    masks = list(resf[1].values())
                    demasks = maskUtils.decode(masks).transpose(2,0,1)
                    out = mmcv.visualization.imshow_det_bboxes(im,demasks)
                    import pdb; pdb.set_trace()
                    cv2.imwrite(Do%(i,f), im[::2,::2])
    elif opt == '1.1':
        pass
