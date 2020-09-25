import os,sys
import shutil,glob
import json
from vidtool import videoTool
import numpy as np

if __name__ == "__main__":
    opt = sys.argv[1]
    job_id = 0
    job_num = 1
    if len(sys.argv) > 3:
        job_id = int(sys.argv[2])
        job_num = int(sys.argv[3])

    vtool = videoTool(job_id, job_num)
   
    fn = 'data/video'
    fn = 'data/video_v1'
    vopt=0;vv=['cooking']
    #vopt=0;vv=['music_video']
    #vv=[]
    #fn = 'data/video_v0';vv=[]

    vtool.data.setInputVideoJson(fn + '.json')


    for video_name in vtool.data.video_all_name:
        # Set up the web proofreading for shot detection and classification
        video_genre = video_name[:video_name.rfind('/')]
        video_url = video_name[video_name.rfind('/')+1:]
        if len(vv) > 0 :
            if vopt == 0:
                if video_genre not in vv:
                    continue
            elif vopt == 1:
                if video_url not in vv:
                    continue
        vtool.data.setVideoInfo(video_name)
        print('process video: ', video_name)

        if opt == '0':
            # Prepage images
            vtool.processor.copyFrames(vtool.data.FRAME_NAME.format(video_name, '_ds'), frame_downsample = vtool.video_frame_size[1]//320)
        elif opt == '0.1':
            # Generate htmls/js
            #vtool.webProofreadFolder()
            vtool.setRedo(True)
            #vtool.webProofreadShot()
            #vtool.webProofreadSeg(input_txt ='shot_all')
            vtool.proofreader.webProofreadCluster()

        # Set up desktop (VAST) proofreading
        elif opt == '1': # copy video info
            file_in = 'data/video_v1.json'
            folder_out = vtool.data.FOLDER_VAST
            shutil.copy(file_in, folder_out)
        elif opt == '1.1':
            # Prepage images
            vtool.processor.copyFrames(vtool.data.PROCESSOR_VAST %(video_genre, video_url) + 'im/')
        elif opt == '1.2':
            # Generate shot_bd.vsvi files for VAST
            #vtool.setRedo(True)
            #vtool.proofreader.vastProofreadSeg('all') # all frames
            if video_url in ['3nUKwvFsjA4']:
                continue
            vtool.proofreader.vastProofreadSeg('cluster_selected_list_first') # only first frame per shot/cluster
        
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
        # on web server: copy files: middle/share -> web
        elif opt == '3':
            # refinement for display 
            Di = vtool.video_share_folder % 'seg_ds'
            Do = vtool.video_web_folder % 'seg_ds'
            vutil.copyFolder(Di, Do, frame_downsample=2)
        elif opt == '3.1':
            # refinement for display 
            Di = (vtool.video_share_folder % '') + 'refined_seg/'
            Do = vtool.video_data_folder + 'refined_seg/'
            vutil.copyFolder(Di, Do)
        elif opt == '3.2':
            # rename names
            Do = vtool.video_data_folder + 'refined_seg/'
            fns = sorted(glob.glob(Do + '*.png'))[::-1]
            for fn in fns:
                num = int(fn[fn.rfind('_')+1:-4])
                fn_new = fn[:fn.rfind('_')+1]+('%05d'%(1+num*vtool.video_frame_rate))+fn[-4:]
                shutil.move(fn, fn_new)
