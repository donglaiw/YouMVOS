import os,sys,shutil
import json
from vidtool import videoDownloader
from vidtool import videoUtil as vutil

if __name__ == "__main__":
    opt = sys.argv[1]
    job_id = 0
    job_num = 1
    if len(sys.argv) > 3:
        job_id = int(sys.argv[2])
        job_num = int(sys.argv[3])

    param = json.load(open('data/param.json'))

    vd = videoDownloader(job_id, job_num)
    data_folder = param['DATA_FOLDER']
    web_folder = param['WEB_FOLDER']
    share_folder = param['SHARE_FOLDER']
    ffmpeg = param['FFMPEG']

    vd.setFolders(data_folder, web_folder, share_folder)
    fn = 'data/video_cooking'
    fn = 'data/video'
    #vd.setInputVideoJson(fn + '.json')
    vd.setInputVideoTxt(fn + '.txt')

    for vid,video_name in enumerate(vd.video_all_name[job_id::job_num]):
        print('process video: ', video_name)
        vd.setVideoInfo(video_name)

        if opt == '0':
            # Download the mp4
            vd.getVideoMP4()
        elif opt == '0.1':
            # Check video size
            vutil.checkVideoSize(vd.getVideoPath())
        elif opt == '0.2':
            # Extract frames
            vd.getVideoFrames(ffmpeg)
        elif opt == '0.3':
            # Gather video information: txt -> json
            if vid ==0:
                vutil.VideoTxtToJson(fn + '.txt', fn + '.json', data_folder, data_folder)
            break;
