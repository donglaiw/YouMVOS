import os,sys
import numpy as np

from T_util import readtxt,U_mkdir,getVideoInfo,checkTxtFormat

opt = sys.argv[1]
job_id=0;job_num=1;
if len(sys.argv)>3:
    job_id = int(sys.argv[2])
    job_num = int(sys.argv[3])

Dv='/n/pfister_lab2/Lab/vcg_natural/youtubeE-vis/'
# youtube-dl -f 136
# ffmpeg -i image_%05d.png
if opt[0] == '0': # download
    suf = ''
    suf = '_todo'

    input_file = Dv+'data/video%s.txt'%suf

    if opt == '0': # ffmpeg
        # no conda env
    elif opt == '0.1': # check mp4 size
        for line in videos:
            tmp = line.split(',')
            video = Dv+tmp[0]+'.mp4'
            if os.path.exists(video):
                sz, _ = getVideoInfo(video)
                if '1280x' not in sz:
                    print(tmp[0],sz)
    elif opt == '0.2': # ffmpeg
        videos = videos[::-1]
        for line in videos[job_id::job_num]:
            tmp = line.split(',')
            if not os.path.exists(Dv+tmp[0]+'/frame/image_00001.png'):
                print('process: ',tmp[0])
                U_mkdir(Dv+tmp[0]+'/frame/', 2)
                os.system('/n/home04/donglai/local/bin/ffmpeg -i %s.mp4 %s/frame/'%(Dv+tmp[0],Dv+tmp[0])+'image_%05d.png')
    elif opt == '0.3': # raw txt to json
        from glob import glob
        import json
        output = {}
        for line in videos:
            video_url, video_author, video_title = line[:-1].split(',')
            num_frame = len(glob(Dv+video_url+'/frame/*.png'))
            video_sz, video_fps = getVideoInfo(Dv+video_url+'.mp4')
            output[video_url] = {'author': video_author,
                                 'title': video_title,
                                 'num_frame': num_frame,
                                 'fps': float(video_fps),
                                 'size': [int(x) for x in video_sz.split('x')]}
        json.dump(output, open(Dv+'data/video%s.json'%suf,'w'))

elif opt[0] == '1': # compute stat
    from video_processor import videoProcessor
    import json
    suf = ''
    #suf = '_todo'
    videos_dict = json.load(open(Dv+'data/video%s.json'%suf))
    videos = videos_dict.keys()
    #vp = videoProcessor(job_id, job_num)
    vp = videoProcessor(0, 1)
    video_todo = videos
    # video_todo = ['music_video/RB-RcX5DS5A','kid/F4tHL8reNCs','sports/wgVOgGLtPtc','history/Yocja_N5s1I','howto/j2C8MkY7Co8','vlog/0oPa3GJJDDA','product/dfToHzOmwdI','comedy/qVMW_1aZXRk','cooking/3nUKwvFsjA4','animation/KYniUCGPGLs']
    #video_todo = ['music_video/RB-RcX5DS5A','kid/F4tHL8reNCs','history/Yocja_N5s1I','vlog/0oPa3GJJDDA','comedy/qVMW_1aZXRk']
    video_todo = ['music_video/RB-RcX5DS5A']
    param = {}

    for video in video_todo[job_id::job_num]:
        print('process: ', video)
        def getFrameName(frame_id):
            #print('load %d'%frame_id)
            return Dv+video+'/frame/image_%05d.png'%(1+frame_id)
        vp.setGetFrameName(getFrameName)
        vp.setVideoInfo(Dv+video+'/', videos_dict[video]['num_frame'], videos_dict[video]['fps'], 'db/export/')
        # frame visualization
        if opt =='1': # compute frame difference
            vp.processDownsample()
            vp.visualizeClip()
        # scene detection 
        elif opt =='1.1': # compute frame difference
            vp.computeMaxDiff()
        elif opt =='1.11': # merge frame difference into one file
            vp.computeMaxDiffCombine()
        elif opt =='1.12': # shot detection
            threshold_dark = 50;
            threshold_diff = 20
            if video in param:
                threshold_dark, threshold_diff = param[video]
            vp.computeShot(threshold_dark = threshold_dark, threshold_diff = threshold_diff)
        elif opt =='1.13': # generate html/js file for proofreading
            vp.setRedo(True)
            vp.proofreadShot()
        elif opt =='1.14': # output shot gif
            vp.visualizeShot()
        elif opt =='1.2': # output shot gif
            vp.visualizeResult()

        elif opt =='1.3': # output shot gif
            vp.proofreadSeg()
        elif opt =='1.9': # debug
            #diff = vp.getStat('rgb_diff')
            from glob import glob
            import shutil
            seg = vp.export_folder + 'seg/'
            fns = [x[x.rfind('/')+1:] for x in glob(seg+'*.png')]
            # be carefule: _s can be in the video url..
            for fn in fns:
                shutil.move(seg+fn, seg+fn.replace('_s','seg_'))
