import os,sys
import shutil,glob
import json
from vidtool import videoTool
import numpy as np
from glob import glob

if __name__ == "__main__":
    opt = sys.argv[1]
    job_id = 0
    job_num = 1
    if len(sys.argv) > 3:
        job_id = int(sys.argv[2])
        job_num = int(sys.argv[3])

    vtool = videoTool(job_id, job_num)
   
    fn = 'data/video_v0'
    video_done = vtool.util.readtxt(fn + '.txt')
    video_done = [x[:x.find(',')] for x in video_done]
    fn = 'data/video_v1'
    fn = 'data/video_v2'
    fn = 'data/video'
    vopt=0;vv=['cooking']
    vopt=0;vv=['sports']
    vopt=1;vv=['8GwmRn0_Y-Y']
    vopt=1;vv=['enkRALcdPb0','xESsYrYxVDA']
    vopt=1;vv=['1NIhv6fCqAU','yZLzLVAUJiU','MFNv-FJFGTg','Fhuc6qOGNPc']
    vopt=0;vv=['music_video']
    #fn = 'data/video_v0';vv=[]

    vtool.data.setInputVideoJson(fn + '.json')


    for video_name in vtool.data.video_all_name:
        video_genre = video_name[:video_name.rfind('/')]
        video_url = video_name[video_name.rfind('/')+1:]

        if video_name in video_done:
            continue
        if len(vv) > 0 :
            if vopt == 0:
                if video_genre not in vv:
                    continue
            elif vopt == 1:
                if video_url not in vv:
                    continue
        vtool.data.setVideoInfo(video_name)
        print(video_name)

        # 1. Set up the web proofreading for shot detection and classification
        if opt == '0':
            # Prepage images
            frame_size = vtool.processor.frameSize()
            frame_template = vtool.data.FRAME_NAME_DS.format(video_name)
            vtool.processor.frameCopy(frame_template, frame_downsample = frame_size[1]//320)
            vtool.visualizer.visClipGif(os.path.dirname(frame_template), frame_num = 20)
        elif opt == '0.01':
            #frame_template = vtool.data.PROOFREADER_SEG.format(video_name, 'refine_')
            frame_template = vtool.data.PROOFREADER_SEG.format(video_name, 'overlay_')
            vtool.visualizer.visClipGif(os.path.dirname(frame_template), frame_num = 20, frame_type='seg')
        elif opt == '0.1':
            # Generate htmls/js
            vtool.proofreader.webProofreadFolder()
            #vtool.setRedo(True)
            #vtool.proofreader.webProofreadShot()
            #vtool.proofreader.webProofreadSeg(input_txt ='shot_all')
            #vtool.proofreader.webProofreadCluster()

        # 2. Set up desktop (VAST) proofreading
        elif opt == '1': # copy video info
            file_in = 'data/video_v1.json'
            folder_out = vtool.data.FOLDER_VAST
            shutil.copy(file_in, folder_out)
        elif opt == '1.1':
            # Prepage images
            vtool.processor.frameCopy(vtool.data.FRAME_NAME_VAST.format(video_name))
        elif opt == '1.2':
            # Generate shot_bd.vsvi files for VAST
            #vtool.setRedo(True)
            #vtool.proofreader.vastProofreadSeg('all') # all frames
            frame_ids='' # all frames
            frame_ids = 'cluster_selected_list_min' 
            if video_url in ['G2AvRfxgpL4', 'zl7A-Vbe5N8','o78y1264dD8','jm2r5xzYx-A','016LXFHpFCk','2O7K-8G2nwU','AbBe0MjtN1I']:
                frame_ids = 'shot_min' 
            elif video_url in ['X7bj_LUIY7Y','2fdp8SVOSF4','3opTwpiCZ6c']:
                frame_ids = 'cluster_selected_list_mid' 
            else:
            #['-kaaXz4IgrA','nd40lIYtQmA','4rp2aLQl7vg','tG-IGNvfrg8','x04jgjQ_hLI','NzYtFLpJrQU','cZy6sByBHY0','GVdOB4nA7eI','_6VeZAZdff0','f3CBJLAneCA']:
                frame_ids = 'cluster_selected_list_min' 

            vtool.proofreader.vastProofreadSeg(frame_ids) # only first frame per shot/cluster
        elif opt == '1.3':
            # count number of frames to work on for task assignment
            #frame_ids = 'cluster_selected_list_min' 
            #frame_ids = vtool.data.getFrameIndex(frame_ids)
            #print(len(frame_ids))
            pass

        # round 2
        elif opt[0] == '4': # manual mask display
            # movie_trailer
            #fn = '/seg_all_out/';frame_ids = 'all'; 
            #mask_id_func = lambda x: (x-1)/vtool.data.video_frame_rate
            mask_id_func = None 
            frame_ids = 'cluster_selected_list_min' 
            fn = 'seg_shot_bd';
            if video_genre in ['music_video']:
                frame_ids = 'shot_min'
            if video_url in ['iS1g8G_njx8']:
                frame_ids = 'cluster_selected_list_min' 

            if opt == '4': # manual mask display
                mask_template = vtool.data.FOLDER_DOWNLOAD + video_name + '/' + fn + '/' 
                mask_name = sorted(glob(mask_template + '*.png'))
                if len(mask_name) == 0:
                    print('no seg')
                    continue
                num_pad = len(mask_name[-1][mask_name[-1].rfind('_s')+2:mask_name[-1].rfind('.')])
                mask_template = mask_template + '_s%0'+str(num_pad) + 'd.png'
                if video_genre in ['music_video']:
                    if video_url in ['JGwWNGJdvx8']:
                        shot_txt = np.loadtxt(vtool.data.FRAME_ROOT.format(video_name) + 'shot.txt').astype(int)
                        frame_ids = 1+np.unique(shot_txt[:])
                    else:
                        vsvi = vtool.util.readtxt(vtool.data.PROCESSOR_VAST.format(video_name) + 'im_shot_bd.vsvi')
                        frame_ids = np.array([int(x) for x in vsvi[21][vsvi[21].find(':')+3:-3].split(',')])
                    # all frames
                    #mask_id_func = lambda x: (x-1)/vtool.data.video_frame_rate
                    # shot_bd frames
                    mask_id_func = lambda x: np.where(frame_ids == x)[0]

                vtool.visualizer.visSegPng(output_prefix='manual_', frame_ids = frame_ids, mask_template = mask_template, mask_id_func=mask_id_func)
            elif opt == '4.1': # seg stat
                #vtool.setRedo(True)
                vtool.proofreader.vastProofreadSegStat(seg_folder = fn)
            elif opt == '4.11': # seg stat to character
                #vtool.setRedo(True)
                video_names = [x for x in vtool.data.video_all_name if video_genre in x]
                vtool.proofreader.webProofreadCharacter(video_names, seg_folder = fn)

            elif opt == '4.2': # stm mask display
                if vtool.data.video_url in ['RB-RcX5DS5A','iS1g8G_njx8']:
                    continue
                if vtool.data.video_url not in ['RBumgq5yVrA']:
                    continue
                vtool.visualizer.visSegPng(output_prefix='stm_', frame_ids = 'shot_all')


        
        # on hp03: copy files: hp03 -> middle/share
        elif opt == '2':
            name_replace = []
            # refinement for display 
            Di = vtool.video_share_folder + 'overlays/'
            Do = vtool.video_web_folder % 'seg_ds/'
            name_replace = ['overlay_', 'refine_']

            Di = (vtool.video_share_folder % '') + 'refined_seg/'
            Do = (vtool.video_web_folder % '') + 'refined_seg/'
            name_replace = []
            """
            # shot boundary 
            Di = vtool.video_share_folder + 'seg_shot_bd/'
            Do = (vtool.video_web_folder %'') +'seg_shot_bd/'
            """
            
            # for google drive need to refresh the filesystem
            os.system('ls ' + Di)
            vutil.copyFolder(Di, Do, name_replace=name_replace)
        # check files: middle/share
        elif opt == '2.1':
            # refinement for display 
            Di = vtool.video_share_folder + 'overlays/'
            # shot boundary 
            # Di = vtool.video_share_folder + 'seg_shot_bd/'
            if not os.path.exists(Di):
                print('No',Di)
            else:
                ll = len(glob.glob(Di + '/*.png'))
                if ll == 0:
                    print(Di, ll)
        elif opt == '2.2':
            # on web server: copy files: middle/share -> web
            Di = vtool.video_share_folder % 'seg_ds'
            Do = vtool.video_web_folder % 'seg_ds'
            vutil.copyFolder(Di, Do, frame_downsample=2)
        elif opt == '2.3':
            Di = (vtool.video_share_folder % '') + 'refined_seg/'
            Do = vtool.video_data_folder + 'refined_seg/'
            vutil.copyFolder(Di, Do)
        elif opt == '2.4':
            # rename names
            Do = vtool.video_data_folder + 'refined_seg/'
            fns = sorted(glob.glob(Do + '*.png'))[::-1]
            for fn in fns:
                num = int(fn[fn.rfind('_')+1:-4])
                fn_new = fn[:fn.rfind('_')+1]+('%05d'%(1+num*vtool.video_frame_rate))+fn[-4:]
                shutil.move(fn, fn_new)
