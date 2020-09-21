import os,sys,shutil
import json
from vidtool.videoProcessor import videoProcessor
from vidtool import videoUtil as vutil

if __name__ == "__main__":
    opt = sys.argv[1]
    job_id = 0
    job_num = 1
    if len(sys.argv) > 3:
        job_id = int(sys.argv[2])
        job_num = int(sys.argv[3])

    param = json.load(open('data/param.json'))
    vp = videoProcessor(job_id, job_num)
    data_folder = param['DATA_FOLDER']
    web_folder = param['WEB_FOLDER']
    share_folder = param['SHARE_FOLDER']
    share_folder = '/n/boslfs/LABS/lichtman_lab/Donglai/youtop/share/'
    lib_detectron2_folder = param['LIB_DETECTRON2_FOLDER']
    lib_stm_folder = param['LIB_STM_FOLDER']

    fn = 'data/video'
    fn = 'data/video_v1'
    vopt=1;vv=['9bZkp7q19f0']
    vopt=0;vv=['music_video']
    #fn = 'data/video_v0'

    vp.setFolders(data_folder, web_folder, share_folder)
    vp.setInputVideoJson(fn + '.json')

    for vid,video_name in enumerate(vp.video_all_name[job_id::job_num]):

        if len(vv) > 0 :
            if vopt == 0:
                if video_name[:video_name.rfind('/')] not in vv:
                    continue
            elif vopt == 1:
                if video_name[video_name.rfind('/')+1:] not in vv:
                    continue

        print('process video: ', video_name)
        vp.setVideoInfo(video_name)
        # Set up the web proofreading for shot detection and classification
        if opt == '0':
            vp.setSingleProcess()
            vp.processDownsample()
            vp.visualizeClipGif(frame_num = 20)
        elif opt == '0.1': # generate js param for visualization file
            if vid == 0:
                vutil.VideoTxtToJs(fn + '.txt', web_folder + 'js/%s.js' % fn[fn.rfind('/')+1:])
                break
        elif opt =='0.2': # compute frame difference
            vp.setSingleProcess()
            vp.computeMaxDiff()
        elif opt =='0.21': # merge frame difference into one file
            vp.computeMaxDiffCombine()
        elif opt =='0.3': # shot detection
            threshold_dark = 50;
            threshold_diff = 20
            threshold_shot_len = 1
            vp.computeShot(threshold_dark = threshold_dark, threshold_diff = threshold_diff, threshold_shot_len = threshold_shot_len)

        # Detectron2
        elif opt == '1':
            cmd_file = 'db/run_detectron2.sh'
            if vid == 0:
                vutil.writetxt(cmd_file, ['#/bin/bash'])
            # for movie_tralier, compute for all
            frame_index = 1 # keyframes only
            frame_index = 0 # all frames
            vp.computeDetectron2Seg(lib_detectron2_folder, frame_index = frame_index, \
                                    output_folder = vp.video_share_folder + 'seg/', \
                                    cmd_file = cmd_file)
        elif opt == '1.1': # copy seg result: data_folder -> share_folder
            seg_in = vp.getKeyframeSegmentFolder(vp.video_data_folder, 1)
            seg_out = vp.getKeyframeSegmentFolder(vp.video_share_folder, 1)
            shutil.copytree(seg_in, seg_out)

        # STM
        elif opt == '2':
            cmd_file = 'db/run_stm.sh'
            if vid == 0:
                vutil.writetxt(cmd_file, ['#/bin/bash'])
            # for movie_tralier, compute for all
            index_type = 'cluster'
            if vp.video_genre in ['music_video']:
                index_type = 'shot_all_list'
            if vp.video_url in ['RB-RcX5DS5A','iS1g8G_njx8','RBumgq5yVrA']:
                continue
            vp.computeSTMSeg(lib_stm_folder, index_type = index_type, \
                                    output_folder = vp.video_share_folder + 'seg_prop/', \
                                    cmd_file = cmd_file)
        elif opt == '2.1': # compute display

        elif opt == '9':
            f0 = vp.video_name[:vp.video_name.find('/')]
            f1 = vp.video_name[vp.video_name.find('/')+1:]
            print('mkdir -p',vp.video_share_folder+'im/')
            #print('mv',vp.video_share_folder+'../new/'+f1+'/*.png',vp.video_share_folder+'im/')
