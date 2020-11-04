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
   
    #fn = 'data/video_v0'
    fn = 'data/yt_train'
    video_done = vtool.util.readtxt(fn + '.txt')
    video_done = [x[:x.find(',')] for x in video_done]
    fn = 'data/video_v1'
    fn = 'data/video_v2'
    fn = 'data/video'
    vopt=1;vv=['8GwmRn0_Y-Y']
    vopt=1;vv=['enkRALcdPb0','xESsYrYxVDA']
    vopt=1;vv=['1NIhv6fCqAU','yZLzLVAUJiU','MFNv-FJFGTg','Fhuc6qOGNPc']
    vopt=0;vv=['education']
    vopt=0;vv=['howto']
    vopt=0;vv=['movie_trailer']
    vopt=0;vv=['sports']
    vopt=0;vv=['music_video']
    #fn = 'data/video_v0';vv=[]
    #vopt=0;vv=['kid']
    vv=[]

    vtool.data.setInputVideoJson(fn + '.json')
    
    if float(opt) >= 0 :
        tmp = None
        for video_name in vtool.data.video_all_name:
            video_genre = video_name[:video_name.rfind('/')]
            video_url = video_name[video_name.rfind('/')+1:]

            if len(vv) > 0 :
                if vopt == 0 and video_genre not in vv:
                    continue
                elif vopt == 2 and video_genre in vv:
                    continue
                elif vopt == 1 and video_url not in vv:
                    continue
            vtool.data.setVideoInfo(video_name)

            if video_name not in video_done:
                #pass
                continue
            # print(video_name)

            # 1. Set up the web proofreading for shot detection and classification
            if opt == '0':
                # Prepage images
                frame_size = vtool.processor.frameSize()
                frame_template = vtool.data.FRAME_NAME_DS.format(video_name)
                vtool.processor.frameCopy(frame_template, frame_downsample = frame_size[1]//320, frame_rate=vtool.data.video_frame_rate_out)
                # vtool.visualizer.visClipGif(os.path.dirname(frame_template), frame_num = 20)
            elif opt == '0.01':
                #frame_template = vtool.data.PROOFREADER_SEG.format(video_name, 'refine_')
                frame_template = vtool.data.PROOFREADER_SEG.format(video_name, 'overlay_')
                vtool.visualizer.visClipGif(os.path.dirname(frame_template), frame_num = 20, frame_type='seg')
            elif opt == '0.1':
                # 1 FPS: Generate htmls/js
                vtool.proofreader.webProofreadFolder()
                vtool.setRedo(True)

                #vtool.proofreader.webProofreadShot()
                frame_ids = 'cluster_selected_arr' 
                if video_genre in ['music_video'] and video_url not in ['iS1g8G_njx8']:
                    frame_ids = 'shot_selected' 
                if video_genre in ['movie_trailer']:
                    frame_ids = 'shot_selected' 
                if video_name in video_done:
                    frame_ids = 'shot_selected' 
                if video_url in ['G2AvRfxgpL4', 'zl7A-Vbe5N8','o78y1264dD8','jm2r5xzYx-A','016LXFHpFCk','2O7K-8G2nwU','AbBe0MjtN1I']:
                    frame_ids = 'shot_selected' 

                if video_url in ['qVMW_1aZXRk','0oPa3GJJDDA']:
                    continue
                    #pass
                vtool.proofreader.webProofreadSeg(input_txt = frame_ids + '_out')
                #vtool.proofreader.webProofreadCluster()
            elif opt == '0.11':
                # 6 FPS: Generate htmls/js
                #vtool.setRedo(True)
                if video_url in ['iS1g8G_njx8','cmSbXsFE3l8']:
                    continue
                vtool.proofreader.webProofreadShotSR()

            # 2. Set up desktop (VAST) proofreading
            elif opt == '1': 
                # Prepage images
                vtool.processor.frameCopy(vtool.data.FRAME_NAME_VAST.format(video_name))
            elif opt == '1.1':
                frame_ids='' # 1 FPS
                vtool.proofreader.vastProofreadSeg(frame_ids, frame_suf='_all') # only first frame per shot/cluster
            elif opt == '1.2':
                # Generate shot_bd.vsvi files for VAST
                #vtool.setRedo(True)
                #vtool.proofreader.vastProofreadSeg('all') # all frames
                frame_ids = 'cluster_selected_arr_min' 
                if video_url in ['G2AvRfxgpL4', 'zl7A-Vbe5N8','o78y1264dD8','jm2r5xzYx-A','016LXFHpFCk','2O7K-8G2nwU','AbBe0MjtN1I']:
                    frame_ids = 'shot_min' 
                elif video_url in ['X7bj_LUIY7Y','2fdp8SVOSF4','3opTwpiCZ6c']:
                    frame_ids = 'cluster_selected_arr_mid' 
                else:
                #['-kaaXz4IgrA','nd40lIYtQmA','4rp2aLQl7vg','tG-IGNvfrg8','x04jgjQ_hLI','NzYtFLpJrQU','cZy6sByBHY0','GVdOB4nA7eI','_6VeZAZdff0','f3CBJLAneCA']:
                    frame_ids = 'cluster_selected_arr_min' 
                if video_url not in ['8b0ubLO2MUE']:
                    continue
                vtool.proofreader.vastProofreadSeg(frame_ids) # only first frame per shot/cluster
            elif opt == '1.3':
                # count number of frames to work on for task assignment
                #frame_ids = 'cluster_selected_arr_min' 
                #frame_ids = vtool.data.getFrameIndex(frame_ids)
                #print(len(frame_ids))
                pass

            # round 2
            elif opt[0] == '4': # manual mask display
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
                elif opt in ['4.1', '4.11']: # stm mask display
                    # stm: 1fps label for VAST import
                    # movie_trailer
                    #fn = '/seg_all_out/';frame_ids = 'all'; 
                    #mask_id_func = lambda x: (x-1)/vtool.data.video_frame_rate
                    mask_id_func = None 
                    frame_ids = 'cluster_selected_arr' 
                    fn = 'seg_shot_bd';
                    frame_ids = 'cluster_selected_arr' 
                    if video_genre in ['music_video', 'movie_trailer']:
                        if not video_url in ['iS1g8G_njx8']:
                            frame_ids = 'shot_selected'
                    if video_name in video_done:
                        frame_ids = 'shot_selected'
                    if video_url in ['G2AvRfxgpL4', 'zl7A-Vbe5N8','o78y1264dD8','jm2r5xzYx-A','016LXFHpFCk','2O7K-8G2nwU','AbBe0MjtN1I']:
                        frame_ids = 'shot_selected'

                    mask_id_func = lambda x: (x-1)/vtool.data.video_frame_rate
                    output_prefix = 'stm_'
                    mask_template = None
                    if opt == '4.11':
                        frame_ids = frame_ids + '_out'
                        mask_id_func = lambda x: (x-1)/vtool.data.video_frame_step
                        mask_template = vtool.data.PROCESSOR_STM2.format(video_name)
                        output_prefix = 'stm_out_'

                    if video_url not in ['QOG6DAVFrkc','CfUlR_ghqXk','cZy6sByBHY0']:
                        pass
                        #continue

                    if video_url not in ['1Fg5iWmQjwk']:
                        continue
                    #vtool.setRedo(True)
                    vtool.visualizer.visSegPng(output_prefix=output_prefix, frame_ids = frame_ids, \
                                               mask_id_func=mask_id_func, mask_template = mask_template)
                elif opt == '4.2': # refine output
                    output_prefix = 'refine_'
                    frame_ids = 'all_out'
                    mask_template = vtool.data.FOLDER_RELEASE + 'Annotations/' + video_name.replace('/', '_') + '/%05d.png'
                    vtool.visualizer.visSegPng(output_prefix=output_prefix, frame_ids = frame_ids, \
                                               mask_template = mask_template)
                    import pdb; pdb.set_trace()

                elif opt == '4.3': # seg stat
                    #vtool.setRedo(True)
                    if video_genre in ['movie_trailer']:
                        fn = 'seg_all_out';seg_root = None
                    else:
                        fn = 'seg_prop';seg_root = vtool.data.FOLDER_VAST
                    if video_name in video_done:
                        fn = 'seg_all_out';seg_root = vtool.data.FOLDER_VAST
                    vtool.proofreader.vastProofreadSegStat(seg_folder = fn, seg_root = seg_root)

            elif opt[0] == '5': # round 2-bad
                frame_ids = 'cluster_selected_arr_every-5' 
                if video_url in ['2O7K-8G2nwU']:
                    frame_ids = 'shot_selected_arr_every-5' 
                if tmp is None:
                    tmp = vtool.util.readtxt('db/round2-2/bad.txt')
                    tmp_v = [x[:x.find(',')] for x in tmp]
                    tmp_st = [int(x[x.find(',')+1:-1]) for x in tmp]
                if video_name in tmp_v:
                    st = [tmp_st[x] for x in range(len(tmp_st)) if tmp_v[x]==video_name][0]
                    vtool.setRedo(True)
                    if opt == '5': # create im_r2.vsvi
                            vtool.proofreader.vastProofreadSeg(frame_ids, vsvi_suf='_r2', \
                                                               seg_suf=None, frame_ids_after = st) # only first frame per shot/cluster
                    elif opt == '5.1': # rename file
                        mask_id_func = lambda x: (x-vtool.data.FRAME_OFFSET)//vtool.data.video_frame_rate
                        Di = vtool.data.PROCESSOR_STM.format(video_name)
                        Do = vtool.data.FOLDER_VAST + video_name + '/seg_r2/seg_%05d.png'
                        vtool.util.mkdir(Do)
                        #print('rm '+Do[:Do.rfind('/')+1]+'*.png')
                        #continue
                        frame_id = vtool.data.getFrameIndex(frame_ids) 
                        frame_id = frame_id[frame_id > st]
                        for i in range(len(frame_id)):
                            sn = Di%mask_id_func(frame_id[i])
                            if os.path.exists(sn):
                                shutil.copy(sn, Do%i)
                    
                    

            elif opt[0] == '6': # round 3
                import imageio
                if opt == '6': # manual change
                    mask_template = vtool.data.FOLDER_RELEASE + 'Annotations/' + video_name.replace('/', '_') + '/%05d.png'
                    if video_url not in ['1Fg5iWmQjwk']:
                        continue
                    inds = range(661,686,4)
                    for ind in inds:
                        seg = imageio.imread(mask_template % ind)
                        seg[seg==1] = 2
                        imageio.imwrite(mask_template % ind, seg)
                elif opt == '6.1': # manual change
                    mask_template = vtool.data.PROCESSOR_STM2.format(video_name)
                    if video_url not in ['1Fg5iWmQjwk']:
                        continue
                    inds = range(165,172)
                    for ind in inds:
                        seg = imageio.imread(mask_template % ind)
                        seg[seg==1] = 2
                        imageio.imwrite(mask_template % ind, seg)

                    


    if opt =='-1':
        video_names = vtool.data.video_all_name
        video_genres = [video_name[:video_name.rfind('/')] for video_name in video_names]
        video_genre, video_id = np.unique(video_genres, return_inverse = True)
        for ii in np.unique(video_id): 
            vtool.setRedo(True)
            video_names_i = [video_names[x] for x in np.where(video_id == ii)[0]]
            import pdb; pdb.set_trace()
            vtool.data.setVideoInfo(video_names_i[0])
            if video_genre[ii] in ['movie_trailer']:
                fn = 'seg_all_out'; pref='manual_'
            else:
                fn = 'seg_prop';pref='stm_'
            vtool.proofreader.webProofreadCharacter(video_names_i, seg_folder = fn, seg_pref = pref)
