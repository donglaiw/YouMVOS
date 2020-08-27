import os,sys,shutil
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
    web_folder = '/var/www/html/donglai/movie/'
    share_folder = param['SHARE_FOLDER']

    vp.setFolders(data_folder, web_folder, share_folder)

    #vp.setInputVideoTxt('data/video_v0.txt')
    #video_v0 = vp.video_all_name
    vp.setInputVideoJson('data/video.json')


    for video_name in vp.video_all_name:
    #for video_name in video_v0:
        print('process video: ', video_name)
        vp.setVideoInfo(video_name)
        # Set up the web proofreading for shot detection and classification
        if opt == '0':
            # Prepage images
            vp.copyFrames(vp.video_web_folder % 'frame_ds/', frame_downsample = vp.video_frame_size[1]//320)
        elif opt == '0.01': # clean up
            import pdb; pdb.set_trace()
        elif opt == '0.1':
            # Generate htmls/js
            #vp.webProofreadFolder()
            vp.webProofreadShot()
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
            if 'music' not in video_name:
                continue
            import pdb; pdb.set_trace()
            vp.copyFrames('db/export/' + self.video_url + 'im/')
            #vp.copyFrames(vp.video_share_folder + 'im/')
        elif opt == '1.2':
            # Generate vsvi files for VAST
            vp.setRedo(True)
            vp.vastProofreadSeg(frame_index = 1)
        elif opt == '1.3':
            # Generate shot.txt from shot.js
            js_out = vp.getShotTxt(vp.video_share_folder)
            if not os.path.exists(js_out):
                js_in = vp.getShotJs()
                shots, shot_selection = vp.convertShotJsToArr(js_in, 2)
                np.savetxt(js_out, shots[shot_selection == 0], '%d')
        elif opt == '1.4':
            # rename seg_out/images
            from glob import glob
            Do = vp.video_share_folder
            if os.path.exists(Do + 'seg_out/') and not os.path.exists(Do + 'seg.vsseg'):
                print(Do)
                Dw = vp.video_web_folder.replace('movie///%s','movie/download')
                fid = np.loadtxt(Dw + 'fid.txt').astype(int)
                ims = sorted(glob(Do + 'seg_out/*.png')) 
                assert len(ims) == len(fid)
                Do2 = Do + 'seg_out_all/'
                import pdb; pdb.set_trace()
                vutil.mkdir(Do2)
                frames = range(0, vp.video_frame_num, vp.video_frame_rate)
                for i in range(len(fid)):
                    print(np.where(frames == fid[i])[0][0])
                    shutil.copy(ims[i], Do2 + '%04d.png' % np.where(frames == fid[i])[0][0])
        elif opt == '1.5':
            # Refine the seg with grabcut
            pass


        elif opt == '2':
            f0 = vp.video_name[:vp.video_name.find('/')]
            f1 = vp.video_name[vp.video_name.find('/')+1:]
            print('mkdir -p',vp.video_share_folder+'im/')
            #print('mv',vp.video_share_folder+'../new/'+f1+'/*.png',vp.video_share_folder+'im/')
