import os,sys,shutil
from glob import glob
import numpy as np
from vidtool import videoTool

if __name__ == "__main__":
    opt = sys.argv[1]
    job_id = 0
    job_num = 1
    if len(sys.argv) > 3:
        job_id = int(sys.argv[2])
        job_num = int(sys.argv[3])

    vtool = videoTool(job_id, job_num)

    fn = 'data/video_v0'
    fn = 'data/yt_train'
    video_done = vtool.util.readtxt(fn + '.txt')
    video_done = [x[:x.find(',')] for x in video_done]

    fn = 'data/video_v1'
    fn = 'data/video_v2'
    fn = 'data/video'
    vopt=0;vv=['pet']
    vopt=0;vv=['education','product','howto','cartoon','tv']
    vopt=1;vv=['746NhRSrNOY']
    vopt=1;vv=['1NIhv6fCqAU','yZLzLVAUJiU','MFNv-FJFGTg','Fhuc6qOGNPc']
    vopt=0;vv=['education']
    vopt=0;vv=['sports']
    vopt=0;vv=['cooking']
    vopt=0;vv=['howto']
    vopt=0;vv=['movie_trailer']
    vopt=0;vv=['music_video']
    fn = 'data/video_v0';vv=[]
    vtool.data.setInputVideoJson(fn + '.json')
    
    tmp_start = 0
    for vid,video_name in enumerate(vtool.data.video_all_name):
        if video_name not in video_done:
            continue
            #pass
        video_genre = video_name[:video_name.rfind('/')]
        video_url = video_name[video_name.rfind('/')+1:]
        if len(vv) > 0 :
            if vopt == 0 and video_genre not in vv:
                continue
            elif vopt == 2 and video_genre in vv:
                continue
            elif vopt == 1 and video_url not in vv:
                continue
            elif vopt == -1 and video_url in vv:
                continue

        print(video_name)
        vtool.data.setVideoInfo(video_name)

        frame_ids = 'cluster_selected_list_min' 
        if video_genre in ['movie_trailer', 'music_video']:
            frame_ids = 'shot_selected_list' 
        if video_name in video_done:
            frame_ids = 'shot_selected_list' 

        if video_url in ['G2AvRfxgpL4', 'zl7A-Vbe5N8','o78y1264dD8','jm2r5xzYx-A','016LXFHpFCk','2O7K-8G2nwU','AbBe0MjtN1I']:
            frame_ids = 'shot_selected_list' 
        elif video_url in ['-kaaXz4IgrA','nd40lIYtQmA','4rp2aLQl7vg','tG-IGNvfrg8','x04jgjQ_hLI','NzYtFLpJrQU','cZy6sByBHY0','GVdOB4nA7eI','_6VeZAZdff0','f3CBJLAneCA']:
            frame_ids = 'cluster_selected_list_min' 
        elif video_url in ['X7bj_LUIY7Y','2fdp8SVOSF4','3opTwpiCZ6c']:
            frame_ids = 'cluster_selected_list_mid' 

        # Set up the web proofreading for shot detection and classification
        if opt == '0':# shot detection
            vtool.processor.shotDetection()
        elif opt =='0.3': # cluster frames
            #vtool.setRedo(True)
            frame_template = vtool.data.FRAME_NAME_DS.format(vtool.data.video_name)
            vtool.processor.frameCluster(frame_template)

        elif opt == '0.4':
            from glob import glob
            kk='tv'
            kk='howto'
            fns= glob('/n/boslfs02/LABS/lichtman_lab/glichtman/public/vcg/youtop-vis/youtube/proofread/%s/saved/*cluster.js'%kk)
            fns = [x[x.rfind('/')+1:x.rfind('_')] for x in fns]
            vns = [x[x.rfind('/')+1:] for x in vtool.data.video_all_name if kk in x]
            out = list(set(fns) - set(vns))
            for oo in out:
                print('mv %s_cluster.html bk/'%oo)
            import pdb; pdb.set_trace()
        elif opt =='0.5': # black frames
            vtool.processor.computeBlackFrame(thres_black=30)
        elif opt =='0.6': # refine seg
            if video_url in ['iS1g8G_njx8','qVMW_1aZXRk','0oPa3GJJDDA']:
                continue
            mask_id_func = lambda x: (x-vtool.data.FRAME_OFFSET)/vtool.data.video_frame_step
            valid_ran = np.loadtxt(vtool.data.FRAME_ROOT.format(video_name) + 'black_frame30.txt').astype(int)
            vtool.processor.segRefinement(mask_id_func=mask_id_func, valid_ran=valid_ran)

        # Detectron2
        elif opt == '1':
            cmd_file = 'db/run_detectron2.sh'
            if tmp_start == 0:
                os.remove(cmd_file)
                vtool.util.writetxt(cmd_file, ['#/bin/bash'])
                tmp_start = 1
            if video_url not in ['8b0ubLO2MUE']:
                continue
            # for movie_tralier, compute for all
            frame_ids = frame_ids + 'A'
            vtool.processor.segDetectron2(frame_ids = frame_ids, cmd_file = cmd_file)

        # STM
        elif opt == '2.0':# check input seg_shot_bd/ file number
            frame_ids_stm = frame_ids.replace('_list','') + 'A'
            frame_ids = vtool.data.loadClusterJs(option=frame_ids_stm)
            num_cluster = len(frame_ids)
            import pdb; pdb.set_trace()

        elif opt == '2':
            cmd_file = 'db/run_stm2.sh'
            #vtool.setRedo(True)
            if video_url not in ["ZlxIEWygQYY","OPf0YbXqDm0","cZy6sByBHY0","QOG6DAVFrkc","CfUlR_ghqXk","ScgkiTz4nPk","noHAYjTjJKw","lHzTcRqSOhc","ct5Q73pgVMA","wkuDpfiDPYs"]:
                continue
            if tmp_start == 0:
                vtool.util.writetxt(cmd_file, ['#/bin/bash'])
                tmp_start= 1
            frame_ids_stm = frame_ids + 'A_factor'
            vtool.processor.segSTM(frame_ids = frame_ids_stm, cmd_file = cmd_file, stm_len=100)
        elif opt == '2.01': # check output file number
            # desired output
            frame_ids_stm = frame_ids + 'A'
            frame_ids = vtool.data.getFrameIndex(frame_ids_stm)
            mask_name = vtool.data.PROCESSOR_STM.format(vtool.data.video_name)
            mask_name = mask_name[:mask_name.rfind('/')+1]
            # actual output
            num_mask = len(glob(mask_name + '*.png'))
            diff = len(frame_ids) - num_mask 
            if diff<0 or diff>20 :
                print('diff:',video_name,num_mask,len(frame_ids))
                #import pdb; pdb.set_trace()
        elif opt == '2.1':
            cmd_file = 'db/run_stm_out.sh'
            if video_url in ['iS1g8G_njx8','qVMW_1aZXRk','0oPa3GJJDDA']:
                continue
            if tmp_start == 0:
                vtool.util.writetxt(cmd_file, ['#/bin/bash'])
                tmp_start= 1
            frame_ids_stm = frame_ids + 'A_factor_out'
            mask_folder = vtool.data.PROCESSOR_VAST.format(video_name) + 'seg_prop_pf/'
            output_template = vtool.data.PROCESSOR_STM2.format(video_name)
            vtool.processor.segSTM(frame_ids = frame_ids_stm, cmd_file = cmd_file, \
                                  output_template = output_template, \
                                  mask_folder = mask_folder, stm_anchor_num = 2)
        elif opt == '2.9': # check file date
            pass
            import datetime
            if video_genre not in ['education']:
                continue
            frame_ids_stm = frame_ids + 'A'
            frame_ids = vtool.data.getFrameIndex(frame_ids_stm)
            mask_name = vtool.data.PROCESSOR_STM.format(vtool.data.video_name)
            mask_name = mask_name[:mask_name.rfind('/')+1]
            fns = glob(mask_name + '*.png')
            for fn in fns:
                tt = datetime.datetime.fromtimestamp(os.path.getmtime(fn))
                if tt.month == 10 and tt.day==22:
                    os.remove(fn)
                    print(fn)


        elif opt == '9':
            f0 = vtool.video_name[:vtool.video_name.find('/')]
            f1 = vtool.video_name[vtool.video_name.find('/')+1:]
            print('mkdir -p',vtool.video_share_folder+'im/')
            #print('mv',vtool.video_share_folder+'../new/'+f1+'/*.png',vtool.video_share_folder+'im/')

"""
for i in `ls`;do mv $i/seg_all_out/ $i/seg_prop_pf/;done
"""
