import os,sys
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
    vpf = videoProofreader(job_id, job_num)
    data_folder = param['DATA_FOLDER']
    web_folder = param['WEB_FOLDER']
    share_folder = param['SHARE_FOLDER']

    vpf.setFolders(data_folder, web_folder, share_folder)
    vpf.setInputVideoJson('data/video_todo.json')

    for video_name in vpf.video_all_name:
        print('process video: ', video_name)
        vpf.setVideoInfo(video_name)
        # Set up the web proofreading for shot detection and classification
        if opt == '0':
            # Prepage images
            vpf.copyFrames(vpf.video_web_folder, frame_downsample = 4)
        elif opt == '0.1':
            # Generate htmls/js
            vpf.webProofreadShot()
        elif opt == '0.2':
            # Copy final js result: web -> data
            js_in = vp.getShotJS()
            js_out = vp.getShotJS(vp.video_data_folder)
            import pdb; pdb.set_trace()
            shutil.copy(js_in, js_out)

        # Set up desktop (VAST) proofreading
        elif opt == '1':
            # Prepage images
            vpf.copyFrames(vpf.video_share_folder + 'im/')
        elif opt == '1.1':
            # Generate vsvi files for VAST
            vpf.vastProofreadSeg(frame_index = -1)

        elif opt == '2':
            f0 = vpf.video_name[:vpf.video_name.find('/')]
            f1 = vpf.video_name[vpf.video_name.find('/')+1:]
            print('mkdir -p',vpf.video_share_folder+'im/')
            #print('mv',vpf.video_share_folder+'../new/'+f1+'/*.png',vpf.video_share_folder+'im/')
