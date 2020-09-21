import os,sys
import shutil,glob
import json
from vidtool.videoProofreader import videoProofreader
from vidtool import videoUtil as vutil
import numpy as np

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
    #web_folder = '/n/boslfs/LABS/lichtman_lab/Donglai/youtop/web/'

    vp.setFolders(data_folder, web_folder, share_folder)
    
    fn = 'data/video'
    fn = 'data/video_v1'
    vopt=1;vv=['9bZkp7q19f0']
    vopt=0;vv=['cooking']
    vopt=0;vv=['music_video']
    vv=[]
    
    fn = 'data/video_v0';vv=[]

    #vp.setInputVideoTxt('data/video_v0.txt')
    #video_v0 = vp.video_all_name
    vp.setInputVideoJson(fn + '.json')


    for video_name in vp.video_all_name:
    #for video_name in video_v0:
        # Set up the web proofreading for shot detection and classification
        if len(vv) > 0 :
            if vopt == 0:
                if video_name[:video_name.rfind('/')] not in vv:
                    continue
            elif vopt == 1:
                if video_name[video_name.rfind('/')+1:] not in vv:
                    continue
        vp.setVideoInfo(video_name)
        print('process video: ', video_name)

        if opt == '0':
            # Prepage images
            vp.copyFrames(vp.video_web_folder % 'frame_ds/', frame_downsample = vp.video_frame_size[1]//320)
        elif opt == '0.1':
            # Generate htmls/js
            #vp.webProofreadFolder()
            vp.setRedo(True)
            #vp.webProofreadShot()
            #vp.webProofreadSeg(input_txt ='shot_all')
            vp.webProofreadCluster()
        elif opt == '0.2':
            # Copy final js result: web -> data
            js_in = vp.getShotJs()
            js_out = vp.getShotJs(vp.video_data_folder)
            shutil.copy(js_in, js_out)

        # Set up desktop (VAST) proofreading
        elif opt == '1': # copy video info
            file_in = 'data/video.json'
            folder_out = vp.share_folder
            shutil.copy(file_in, folder_out)
        elif opt == '1.1':
            # Prepage images
            vp.copyFrames(vp.video_share_folder + 'im/')
        elif opt == '1.2':
            # Generate shot.txt from shot.js
            js_out = vp.getShotTxt(vp.video_share_folder)
            if not os.path.exists(js_out):
                print('do it', video_name)
                js_in = vp.getShotJs()
                shots, shot_selection = vp.convertShotJsToArr(js_in, 2)
                vutil.mkdir(js_out, 1)
                np.savetxt(js_out, shots[shot_selection == 0], '%d')
        elif opt == '1.3':
            # Generate shot_bd.vsvi files for VAST
            vp.setRedo(True)
            vp.vastProofreadSeg(frame_index = 0) # all frames
            #vp.vastProofreadSeg(frame_index = 1) # only first frame per shot
        elif opt == '1.4':
            # rename seg_out/images
            Do = vp.video_share_folder
            if os.path.exists(Do + 'seg_out/') and not os.path.exists(Do + 'seg.vsseg'):
                print(Do)
                Dw = vp.video_web_folder.replace('movie///%s','movie/download')
                fid = np.loadtxt(Dw + 'fid.txt').astype(int)
                ims = sorted(glob.glob(Do + 'seg_out/*.png')) 
                assert len(ims) == len(fid)
                Do2 = Do + 'seg_out_all/'
                vutil.mkdir(Do2)
                frames = range(0, vp.video_frame_num, vp.video_frame_rate)
                for i in range(len(fid)):
                    print(np.where(frames == fid[i])[0][0])
                    shutil.copy(ims[i], Do2 + '%04d.png' % np.where(frames == fid[i])[0][0])

        elif opt == '1.5':
            # Refine the seg with grabcut
            # TODO: add Sid's code
            if 'F4tHL8reNCs' in video_name:
                vp.RefineSeg(iter_image = 30, iter_algo = 20)
        
        # on hp03: copy files: hp03 -> middle/share
        elif opt == '2':
            name_replace = []
            # refinement for display 
            Di = vp.video_share_folder + 'overlays/'
            Do = vp.video_web_folder % 'seg_ds/'
            name_replace = ['overlay_', 'refine_']

            Di = (vp.video_share_folder % '') + 'refined_seg/'
            Do = (vp.video_web_folder % '') + 'refined_seg/'
            name_replace = []
            """
            # shot boundary 
            Di = vp.video_share_folder + 'seg_shot_bd/'
            Do = (vp.video_web_folder %'') +'seg_shot_bd/'
            """
            
            # for google drive need to refresh the filesystem
            os.system('ls ' + Di)
            vutil.copyFolder(Di, Do, name_replace=name_replace)
        # check files: middle/share
        elif opt == '2.1':
            # refinement for display 
            Di = vp.video_share_folder + 'overlays/'
            # shot boundary 
            # Di = vp.video_share_folder + 'seg_shot_bd/'
            if not os.path.exists(Di):
                print('No',Di)
            else:
                ll = len(glob.glob(Di + '/*.png'))
                if ll == 0:
                    print(Di, ll)
        # on web server: copy files: middle/share -> web
        elif opt == '3':
            # refinement for display 
            Di = vp.video_share_folder % 'seg_ds'
            Do = vp.video_web_folder % 'seg_ds'
            vutil.copyFolder(Di, Do, frame_downsample=2)
