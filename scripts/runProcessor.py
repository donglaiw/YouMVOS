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
    detectron2_folder = param['DETECTRON2_FOLDER']

    vp.setFolders(data_folder, web_folder, share_folder)
    vp.setInputVideoJson('data/video_todo.json')

    for vid,video_name in enumerate(vp.video_all_name[job_id::job_num]):
        print('process video: ', video_name)
        vp.setVideoInfo(video_name)
        # Set up the web proofreading for shot detection and classification
        if opt == '0':
            pass

        # Segmentation: Detectron2
        elif opt == '1':
            cmd_file = 'db/tmp.sh'
            if vid == 0:
                vutil.writetxt(cmd_file, ['#/bin/bash'])
            vp.computeDetectron2Seg(detectron2_folder, 1, \
                                    output_folder = vp.getKeyframeSegmentFolder(vp.video_data_folder, 1), \
                                    shot_file = vp.video_data_folder,
                                    cmd_file = cmd_file)
        elif opt == '1.1': # copy seg result: data_folder -> share_folder
            seg_in = vp.getKeyframeSegmentFolder(vp.video_data_folder, 1)
            seg_out = vp.getKeyframeSegmentFolder(vp.video_share_folder, 1)
            shutil.copytree(seg_in, seg_out)
        elif opt == '2':
            f0 = vp.video_name[:vp.video_name.find('/')]
            f1 = vp.video_name[vp.video_name.find('/')+1:]
            print('mkdir -p',vp.video_share_folder+'im/')
            #print('mv',vp.video_share_folder+'../new/'+f1+'/*.png',vp.video_share_folder+'im/')
