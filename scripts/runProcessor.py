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
    fn = 'data/yt_val'
    #fn = 'db/round2-2/bad'
    #fn = 'db/round2-2/bad_v2'
    fn = 'data/yt_test'


    fn = 'db/round2-2/bad_v4'
    video_done_all = vtool.util.readtxt(fn + '.txt')
    video_done = [x[:x.find(',')] for x in video_done_all]

    #video_done = ['howto/qsxcVsFDDoA','product/4RtNDHPq2V4']
    fn = 'data/video_v1'
    fn = 'data/video_v2'
    fn = 'data/video'
    fn = 'data/video_r2'
    vopt=0;vv=['education','product','howto','cartoon','tv']
    vopt=1;vv=['746NhRSrNOY']
    vopt=1;vv=['1NIhv6fCqAU','yZLzLVAUJiU','MFNv-FJFGTg','Fhuc6qOGNPc']
    vopt=0;vv=['howto']
    vopt=0;vv=['movie_trailer','music_video','cooking','education','pet']
    #vopt=0;vv=['pet']
    #vopt=0;vv=['cooking']
    #vopt=0;vv=['education']
    #vopt=0;vv=['movie_trailer']
    #vopt=0;vv=['music_video']
    #vopt=0;vv=[]
    vopt=0;vv=['sports','tv']
    vopt=0;vv=['kid']
    vopt=0;vv=['howto']
    vopt=0;vv=['product']
    #fn = 'data/video_v0';vv=[]
    vtool.data.setInputVideoJson(fn + '.json')
    vv=[]
    
    vopt=1;vv=['ozgcKw4MyvY','7GV-pQ00PCs','G5frRzhSNJ8','mnYSMhR3jCI']
    
    tmp_start = 0
    # parallel within each video
    #vtool.data.video_all_name = vtool.data.video_all_name[::-1]
    for vid,video_name in enumerate(vtool.data.video_all_name):
    #for vid,video_name in enumerate(vtool.data.video_all_name[job_id::job_num]):
        if video_name not in video_done:
            # continue
            pass
        #print(video_name)
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

        vtool.data.setVideoInfo(video_name)

        frame_ids = 'cluster_selected_list_min' 
        if video_genre in ['movie_trailer', 'music_video']:
            if video_url not in ['iS1g8G_njx8']:
                frame_ids = 'shot_selected_list' 

        if video_url in ['G2AvRfxgpL4', 'zl7A-Vbe5N8','o78y1264dD8','jm2r5xzYx-A','016LXFHpFCk','2O7K-8G2nwU','AbBe0MjtN1I']:
            frame_ids = 'shot_selected_list' 
        elif video_url in ['-kaaXz4IgrA','nd40lIYtQmA','4rp2aLQl7vg','tG-IGNvfrg8','x04jgjQ_hLI','NzYtFLpJrQU','cZy6sByBHY0','GVdOB4nA7eI','_6VeZAZdff0','f3CBJLAneCA']:
            frame_ids = 'cluster_selected_list_min' 
        elif video_url in ['X7bj_LUIY7Y','2fdp8SVOSF4','3opTwpiCZ6c']:
            frame_ids = 'cluster_selected_list_mid' 

        # Set up the web proofreading for shot detection and classification
        if opt == '0':# shot detection
            vtool.setSingleProcess()
            print(video_name)
            if not os.path.exists(vtool.data.FOLDER_DOWNLOAD.format(video_name) + 'rgb_max.txt'):
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
        elif opt =='0.5': # black frames
            vtool.processor.computeBlackFrame(thres_black=30)
        elif opt =='0.6': # refine seg
            vtool.setRedo(False)
            mask_id_func = lambda x: (x-vtool.data.FRAME_OFFSET)/vtool.data.video_frame_step
            valid_ran = np.loadtxt(vtool.data.FOLDER_DOWNLOAD.format(video_name) + 'black_frame30.txt').astype(int)
            vtool.processor.segRefinement(mask_id_func=mask_id_func, valid_ran=valid_ran)

        # Detectron2
        elif opt == '1':
            cmd_file = 'db/run_detectron2.sh'
            if tmp_start == 0:
                if os.path.exists(cmd_file):
                    os.remove(cmd_file)
                vtool.util.writetxt(cmd_file, ['#/bin/bash'])
                tmp_start = 1
            """
            if video_url not in ['wk7qkgS-TTg']:
                continue
            """
            # for movie_tralier, compute for all
            frame_ids = frame_ids + 'A_arr'
            frame_ids = 'all'
            #frame_ids = 'cluster_selected_min'
            vtool.processor.segDetectron2(frame_ids = frame_ids, cmd_file = cmd_file)

        # STM
        elif opt == '2.0':# check input seg_shot_bd/ file number
            frame_ids_stm = frame_ids.replace('_list','') + 'A'
            frame_ids = vtool.data.loadClusterJs(option=frame_ids_stm)
            num_cluster = len(frame_ids)
            import pdb; pdb.set_trace()

        elif opt == '2': # seg_shot_bd -> 1FPS
            cmd_file = 'db/run_stm.sh'
            if video_url not in ['JQk56_ZJEOo']:
                continue
            import pdb; pdb.set_trace()
            vtool.setRedo(True)
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
            # 1 FPS -> 6 FPS
            cmd_file = 'db/run_stm_out.sh'
            vtool.setRedo(True)
            vvv = ['product/tQANVXppDPE','education/uyMtsyzXWd4','product/8OJdwuvZWrI']
            vvv = ['sports/8b0ubLO2MUE','cooking/u6TFP_r2oA8','kid/do6EgKG_YUo']
            vvv = ['sports/_6VeZAZdff0','sports/4rp2aLQl7vg','sports/zl7A-Vbe5N8','cooking/ct5Q73pgVMA','tv/Z4SXxxUnq0U','tv/zgIib_Uj1T4','product/wkuDpfiDPYs']
            vvv = ["sports/NzYtFLpJrQU","music_video/7PCkvCPvDXk","product/dfToHzOmwdI","movie_trailer/EcxBrTvLbBM","howto/qsxcVsFDDoA","howto/GibMs1kod2Y","tv/_yl2fV6SM_8","tv/746NhRSrNOY"]
            vvv = ['sports/2O7K-8G2nwU','product/JQk56_ZJEOo','tv/izh-j8KUYjs',"cooking/ScgkiTz4nPk","kid/xqvN9yJeyO0","howto/wk7qkgS-TTg","tv/K_dFhEeuCtM"]
            vvv = ['product/4RtNDHPq2V4']
            vvv = ['cooking/iUtLMkLhUKY','howto/wk7qkgS-TTg']
            if video_name not in vvv:
                continue
                #pass
            print('rm /n/pfister_lab2/Lab/donglai/YouTop200/db/share/%s/seg_prop_out/*.png'%video_name)
            if tmp_start == 0:
                vtool.util.writetxt(cmd_file, ['#/bin/bash'])
                tmp_start= 1
            frame_ids_stm = 'shot_selected_list_out'
            mask_folder = vtool.data.FOLDER_VAST.format(video_name) + 'seg_prop_pf/'
            output_template = vtool.data.PROCESSOR_STM2.format(video_name)
            vtool.processor.segSTM(frame_ids = frame_ids_stm, cmd_file = cmd_file, \
                                  output_template = output_template, \
                                  mask_folder = mask_folder, stm_anchor_num = 2)
        # dense sample -> 1 FPS
        elif opt == '2.2':
            # rename seg files
            video_done = ['product/4RtNDHPq2V4']
            video_done = ['cooking/iUtLMkLhUKY']
            video_done = ['education/Fhuc6qOGNPc']
            if video_name not in video_done:
                continue
            output_folder2 = vtool.data.FOLDER_VAST.format(video_name) + 'seg_r2_pf_rename/'
            vtool.util.mkdir(output_folder2)
            fns = glob(output_folder2 + '/*.png')
            if len(fns) == 0:
                output_folder = vtool.data.FOLDER_VAST.format(video_name) + 'seg_r2_pf/'
                fns = sorted(glob(output_folder + '/*.png'))
                if len(fns) > 0:
                    frame_ids_stm = frame_ids[:frame_ids.rfind('_')] + '_arr_every-10'
                    if video_url in ['4RtNDHPq2V4']:
                        frame_ids_stm = frame_ids[:frame_ids.rfind('_')] + '_arr_every-20'
                    elif video_url in ['iUtLMkLhUKY','Fhuc6qOGNPc']:
                        frame_ids_stm = frame_ids[:frame_ids.rfind('_')] + '_arr_every-5'
                    frame_ids = vtool.data.getFrameIndex(frame_ids_stm)
                    tmp_st = [int(x[x.find(',')+1:-1]) for x in video_done_all if video_name in x][0]
                    # was a bug
                    frame_ids = frame_ids[frame_ids > tmp_st]
                    #frame_ids = frame_ids[frame_ids > 1+tmp_st*vtool.data.video_frame_rate]
                    fid = int(fns[-1][fns[-1].rfind('s')+1:-4])
                    print(fid, len(frame_ids))
                    assert ((len(frame_ids) - fid -1) >= 0) * ((len(frame_ids) - fid -1) <= 2)
                    # if bug: manual copy ...
                    for fn in fns:
                        fid = int(fn[fn.rfind('s')+1:-4])
                        shutil.copy(fn, output_folder2 + 'seg_%05d.png'%frame_ids[fid])

        elif opt == '2.21': # dense sample -> 1 FPS
            cmd_file = 'db/run_stm_dense.sh'
            video_done = ['cooking/iUtLMkLhUKY']
            video_done = ['education/Fhuc6qOGNPc']
            if video_name not in video_done:
                #pass
                continue
            print(video_name)
            if tmp_start == 0:
                vtool.util.writetxt(cmd_file, ['#/bin/bash'])
                tmp_start= 1

            tmp_st = [int(x[x.find(',')+1:-1]) for x in video_done_all if video_name in x][0]
            tmp_st = tmp_st * vtool.data.video_frame_rate + 1
            frame_ids_stm = frame_ids + 'A_factor'
            #frame_ids_stm = frame_ids + 'A_factor_every-10'
            mask_folder = vtool.data.FOLDER_VAST.format(video_name) + 'seg_r2_pf_rename/'
            output_template = vtool.data.PROCESSOR_STM.format(video_name).replace('seg_prop','seg_prop_v2')
            vtool.processor.segSTM(frame_ids = frame_ids_stm, cmd_file = cmd_file, \
                                    output_template = output_template, \
                                    frame_ids_after = tmp_st, stm_len = 60, \
                                    mask_folder = mask_folder, stm_anchor_num = 2, \
                                    mask_step_input = 1, mask_step_input_offset = 0, \
                                    mask_step_output = vtool.data.video_frame_rate, stm_step = vtool.data.video_frame_rate)
        elif opt == '2.22': # copy before tmp_st [done] into 1 FPS
            if video_url not in video_done:
                continue
            tmp_st = [int(x[x.find(',')+1:-1]) for x in video_done_all if video_name in x][0]
            tmp_st = tmp_st * vtool.data.video_frame_rate + 1

            input_folder = vtool.data.FOLDER_VAST.format(video_name) + 'seg_prop_pf/_s%03d.png'
            output_folder = vtool.data.FOLDER_VAST.format(video_name) + 'seg_prop_v2/seg_%05d.png'
            for i in range(tmp_st+1):
                fn = input_folder % i
                sn = output_folder % i
                if os.path.exists(fn) and not os.path.exists(sn):
                    shutil.copy(fn, sn)
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
