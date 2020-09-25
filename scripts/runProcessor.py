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
    vopt=0;vv=['music_video']
    vopt=0;vv=['cooking']
    vopt=1;vv=['iUtLMkLhUKY']
    #vopt=1;vv=['iS1g8G_njx8']
    #fn = 'data/video_v0'

    vtool.data.setInputVideoJson(fn + '.json')

    for vid,video_name in enumerate(vtool.data.video_all_name[job_id::job_num]):
        if len(vv) > 0 :
            if vopt == 0:
                if video_name[:video_name.rfind('/')] not in vv:
                    continue
            elif vopt == 1:
                if video_name[video_name.rfind('/')+1:] not in vv:
                    continue

        print('process video: ', video_name)
        vtool.data.setVideoInfo(video_name)
        # Set up the web proofreading for shot detection and classification
        if opt == '0':
            vtool.setSingleProcess()
            vtool.processor.downsampleFrame()
            vtool.visualizer.visualizeClipGif(frame_num = 20)
        elif opt == '0.1': # generate js param for visualization file
            if vid == 0:
                vutil.VideoTxtToJs(fn + '.txt', web_folder + 'js/%s.js' % fn[fn.rfind('/')+1:])
                break
        elif opt =='0.1': # shot detection
            vtool.processor.shotDetection()
        elif opt =='0.2': # cluster frames
            #vtool.setRedo(True)
            vtool.processor.frameCluster()

        # Detectron2
        elif opt == '1':
            cmd_file = 'db/run_detectron2.sh'
            if vid == 0:
                vtool.util.writetxt(cmd_file, ['#/bin/bash'])
            # for movie_tralier, compute for all
            frame_ids = 1 # keyframes only
            frame_ids = 0 # all frames
            vtool.processor.segDetectron2(frame_ids = frame_ids, cmd_file = cmd_file)
        elif opt == '1.1': # copy seg result: data_folder -> share_folder
            seg_in = vtool.data.getKeyframeSegmentFolder(vtool.video_data_folder, 1)
            seg_out = vtool.data.getKeyframeSegmentFolder(vtool.video_share_folder, 1)
            shutil.copytree(seg_in, seg_out)

        # STM
        elif opt == '2':
            cmd_file = 'db/run_stm.sh'
            if vid == 0:
                vtool.util.writetxt(cmd_file, ['#/bin/bash'])
            # for movie_tralier, compute for all
            frame_ids = 'cluster'
            if vtool.data.video_genre in ['music_video']:
                frame_ids = 'shot_all_list'
            if vtool.data.video_url in ['RB-RcX5DS5A','iS1g8G_njx8']:
                continue
            if vtool.data.video_url not in ['RBumgq5yVrA']:
                continue

            vtool.processor.segSTM(frame_ids = frame_ids, cmd_file = cmd_file)

        elif opt == '2.1': # stm display
            if vtool.data.video_url in ['RB-RcX5DS5A','iS1g8G_njx8']:
                continue
            if vtool.data.video_url not in ['RBumgq5yVrA']:
                continue
            vtool.visualizer.visSegPng(output_prefix='stm_', frame_ids = 'shot_all')

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
