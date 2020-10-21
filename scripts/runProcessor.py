import os,sys,shutil
from vidtool import videoTool

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
    fn = 'data/video_v2'
    vopt=0;vv=['music_video']
    vopt=0;vv=['cooking']
    vopt=0;vv=['sports']
    vopt=0;vv=['pet']
    vopt=0;vv=['education','product','howto','cartoon','tv']
    vopt=1;vv=['746NhRSrNOY']
    vopt=1;vv=['1NIhv6fCqAU','yZLzLVAUJiU','MFNv-FJFGTg','Fhuc6qOGNPc']
    vopt=0;vv=['howto']
    #fn = 'data/video_v0'

    vtool.data.setInputVideoJson(fn + '.json')

    for vid,video_name in enumerate(vtool.data.video_all_name[job_id::job_num]):
        video_genre = video_name[:video_name.rfind('/')]
        video_url = video_name[video_name.rfind('/')+1:]
        if len(vv) > 0 :
            if vopt == 0:
                if video_genre not in vv:
                    continue
            elif vopt == 1:
                if video_url not in vv:
                    continue
            elif vopt == -1:
                if video_url in vv:
                    continue
        if video_url in ['F4tHL8reNCs','KYniUCGPGLs','dfToHzOmwdI','qVMW_1aZXRk','0oPa3GJJDDA','j2C8MkY7Co8']:
            continue
        print('process video: ', video_name)
        vtool.data.setVideoInfo(video_name)
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

        # Detectron2
        elif opt == '1':
            cmd_file = 'db/run_detectron2.sh'
            if vid == 0:
                vutil.remove(cmd_file)
                vtool.util.writetxt(cmd_file, ['#/bin/bash'])
            if video_url in ['Yocja_N5s1I']:
                continue

            frame_ids = 'cluster_selected_list_min' 
            if video_url in ['wgVOgGLtPtc','8b0ubLO2MUE']:
                continue
            if video_url in ['G2AvRfxgpL4', 'zl7A-Vbe5N8','o78y1264dD8','jm2r5xzYx-A','016LXFHpFCk','2O7K-8G2nwU','AbBe0MjtN1I']:
                frame_ids = 'shot_min' 
            elif video_url in ['-kaaXz4IgrA','nd40lIYtQmA','4rp2aLQl7vg','tG-IGNvfrg8','x04jgjQ_hLI','NzYtFLpJrQU','cZy6sByBHY0','GVdOB4nA7eI','_6VeZAZdff0','f3CBJLAneCA']:
                frame_ids = 'cluster_selected_list_min' 
            elif video_url in ['X7bj_LUIY7Y','2fdp8SVOSF4','3opTwpiCZ6c']:
                frame_ids = 'cluster_selected_list_mid' 

            if frame_ids == 'cluster_selected_list_mid':
                continue

            # for movie_tralier, compute for all
            vtool.processor.segDetectron2(frame_ids = frame_ids, cmd_file = cmd_file)

        # STM
        elif opt == '2':
            cmd_file = 'db/run_stm.sh'
            if vid == 0:
                vtool.util.writetxt(cmd_file, ['#/bin/bash'])
            # for movie_tralier, compute for all
            frame_ids = 'cluster_selected_list_min'
            vtool.processor.segSTM(frame_ids = frame_ids, cmd_file = cmd_file)
            import pdb; pdb.set_trace()

        elif opt == '2.11': # check stm size
            if vtool.data.video_url in ['RB-RcX5DS5A','JGwWNGJdvx8','iS1g8G_njx8','RBumgq5yVrA','bnVUHWCynig']:
                continue
            import imageio
            frame_ids = vtool.data.getFrameIndex('shot_all')
            for frame_id in frame_ids: 
                mask_name = vtool.data.PROCESSOR_STM.format(vtool.data.video_name) % frame_id
                if os.path.exists(mask_name) and imageio.imread(mask_name).shape[0] != 720:
                    print('bug')

        elif opt == '9':
            f0 = vtool.video_name[:vtool.video_name.find('/')]
            f1 = vtool.video_name[vtool.video_name.find('/')+1:]
            print('mkdir -p',vtool.video_share_folder+'im/')
            #print('mv',vtool.video_share_folder+'../new/'+f1+'/*.png',vtool.video_share_folder+'im/')
