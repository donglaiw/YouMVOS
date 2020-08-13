import os,sys,shutil
import json
from vidtool.videoProofreader import videoProofreader

if __name__ == "__main__":
    opt = sys.argv[1]
    job_id = 0
    job_num = 1
    if len(sys.argv) > 3:
        job_id = int(sys.argv[2])
        job_num = int(sys.argv[3])

    param = json.load(open('data/param.json'))
    vp = videoProofreader(job_id, job_num)
    data_folder = param['DATA_FOLDER']
    web_folder = param['WEB_FOLDER']
    share_folder = param['SHARE_FOLDER']

    vp.setFolders(data_folder, web_folder, share_folder)
    vp.setInputVideoJson('data/video_todo.json')

    for video_name in vp.video_all_name:
        print('process video: ', video_name)
        vp.setVideoInfo(video_name)
        # Set up the web proofreading for shot detection and classification
        if opt == '0':
            # Prepage images
            vp.copyFrames(vp.video_web_folder, frame_downsample = 4)
        elif opt == '0.1':
            # Generate htmls/js
            vp.webProofreadShot()
        elif opt == '0.2':
            # Copy final js result: web -> data
            js_in = vp.getShotJs()
            js_out = vp.getShotJs(vp.video_data_folder)
            shutil.copy(js_in, js_out)

        # Set up desktop (VAST) proofreading
        elif opt == '1':
            # Prepage images
            vp.copyFrames(vp.video_share_folder + 'im/')
        elif opt == '1.1':
            # Generate vsvi files for VAST
            vp.vastProofreadSeg(frame_index = -1)

        elif opt == '2':
            f0 = vp.video_name[:vp.video_name.find('/')]
            f1 = vp.video_name[vp.video_name.find('/')+1:]
            print('mkdir -p',vp.video_share_folder+'im/')
            #print('mv',vp.video_share_folder+'../new/'+f1+'/*.png',vp.video_share_folder+'im/')
