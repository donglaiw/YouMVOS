import os, shutil
from glob import glob
from .videoProcessor import videoProcessor
from .videoProofreader import videoProofreader
from .videoVisualizer import videoVisualizer
from .videoData import videoData
from . import videoUtil as vutil
import numpy as np

class videoTool(object):
    def __init__(self, videos_txt='', project_txt=''):
        self.proofreader = videoProofreader()
        self.processor = videoProcessor()
        self.visualizer = videoVisualizer()
        self.data = videoData()
        self.setVideoList(videos_txt)
        self.setProjectParam(project_txt)

    
    def setRedo(self, redo):
        self.proofreader.setRedo(redo)
        self.processor.setRedo(redo)
        self.visualizer.setRedo(redo)
    
    def setVideoList(self, videos_txt):
        if len(videos_txt) > 0:
            self.data.setVideoList(videos_txt)

    def setProjectParam(self, project_txt):
        if len(project_txt) > 0:
            self.data.setProjectParam(project_txt)
            self.proofreader.setFolderInfo(self.data.web_proofread_folder, self.data.FRAME_OFFSET)
            self.processor.setLibInfo(self.data.LIB_DETECTRON2, self.data.LIB_STM)

    def process(self, cmd='', job_id = 0, job_num = 1):
        option_cluster = 'cluster_selected_mid'
        if cmd == 'extract-info':
            self.data.extractVideoInfo()
        else:
            self.data.setVideoJson()
            videos_todo = self.data.videos_name[job_id::job_num]
            if '@' in cmd:
                cmd, videos_todo = cmd.split('@')
                videos_todo = videos_todo.split(',')
            # parallized jobs
            for vid,video_name in enumerate(videos_todo):
                if video_name in ['']:
                    continue
                self.data.setVideo(video_name)
                if not 'print' in cmd:
                    print('process: ', video_name)
                if cmd == 'download':
                    # update: youtube-dl -U
                    self.processor.downloadVideo(self.data.video_url, self.data.video_folder)
                elif 'frame' in cmd:
                    if cmd == 'extract-frame': # video -> all frames
                        self.processor.extractFrames(self.data.LIB_FFMPEG, self.data.video_file, self.data.video_frame_template)

                    elif cmd == 'black-frame': # video -> all frames
                        frame_ids = self.data.getFrameIndex('uniform%d' % self.data.FRAME_SAMPLE_NUM)
                        self.processor.computeBlackFrame(self.data.video_frame_template, frame_ids, self.data.video_stats_black)
                    else:
                        frame_ids = self.data.getFrameIndex()
                        if cmd == 'web-frame':# downsampled frames for web proofreading
                            self.processor.frameCopy(self.data.video_frame_template, self.data.web_frame_template, frame_ids, self.data.frame_size[1]//self.data.WEB_FRAME_WIDTH)
                        elif cmd == 'vast-frame':# downsampled frames for vast proofreading
                            self.processor.frameCopy(self.data.video_frame_template, self.data.vast_frame_template, frame_ids)
                        elif cmd == 'cluster-frame': # for initial manual annotation
                            self.processor.frameCluster(self.data.web_frame_template, frame_ids, self.data.video_stats_cluster)
                        elif cmd == 'release-frame': # for initial manual annotation
                            self.processor.frameCopy(self.data.video_frame_template, self.data.release_frame_template, frame_ids)
                elif 'vast-proofread' in cmd:
                    if cmd == 'vast-proofread-1fps':
                        frame_ids = self.data.getFrameIndex('1fps')
                        self.proofreader.vastProofreadSeg(frame_ids, self.data.frame_size[::-1], self.data.vast_folder, ['im_1fps'], ['im'])
                elif 'web-proofread' in cmd:
                    if cmd == 'web-proofread-cluster':
                        self.proofreader.webProofreadScene(self.data.video_stats_cluster,video_name, self.data.frame_step, self.data.web_frame_template_local)
                    elif cmd == 'web-proofread-shot':
                        self.proofreader.webProofreadScene(self.data.video_stats_shot,video_name, self.data.frame_step, self.data.web_frame_template_local)
                    elif cmd == 'web-proofread-seg-release':
                        # create seg-overlaid png
                        frame_ids = self.data.getFrameIndex()
                        self.visualizer.visSegPng(self.data.web_frame_template, self.data.release_seg_template, self.data.web_proofread_seg.format('r'), frame_ids, mask_downsample=self.data.frame_size[1]//self.data.WEB_FRAME_WIDTH)
                        # create html
                        self.proofreader.webProofreadScene(self.data.video_stats_shot, video_name, self.data.frame_step, self.data.web_proofread_seg_local.format('r'))
                        # link to check the results
                        print(self.data.web_proofread_server.format('shot'))
                elif 'detectron2' in cmd:
                    frame_ids = self.data.getFrameIndex(option_cluster, input_file=self.data.web_proofread_cluster)
                    if cmd == 'detectron2-cluster':
                        cmd_file = 'run_detectron2_%d_%d.sh' % (job_id, job_num)
                        if vid == 0:
                            if os.path.exists(cmd_file):
                                os.remove(cmd_file)
                            vutil.writetxt(cmd_file, ['#/bin/bash'])
                            os.chmod(cmd_file, 0o755)
                        output_template = os.path.join(self.data.vast_detectron2, self.data.SEG_FMT)
                        self.processor.segDetectron2(frame_ids, self.data.video_frame_template, output_template, cmd_file)
                    elif cmd == 'detectron2-vast':
                        self.proofreader.vastProofreadSeg(frame_ids, self.data.frame_size[::-1], self.data.vast_folder, ['im_cluster','seg_cluster'], ['im','seg'])
                elif 'vast-copy' in cmd:
                    # proofread -> copy to final folder
                    # vast-copy-shot_first
                    # vast-copy-shot_every10
                    # vast-copy-cluster
                    cmd_out = cmd[10:]
                    output_mask_template = os.path.join(self.data.vast_stm.format('_all'), self.data.SEG_FMT)
                    vutil.mkdir(output_mask_template, 'parent')
                    if 'cluster' in cmd:
                        fn = self.data.vast_cluster
                        ind = self.data.getFrameIndex(option_cluster, input_file=self.data.web_proofread_cluster)
                    else:
                        fn = self.data.vast_stm.format('_'+cmd_out+'_pf')
                        ind0 = self.data.getFrameIndex(option_cluster, input_file=self.data.web_proofread_cluster)
                        if 'every' in cmd_out or 'all' in cmd_out:
                            ind0 = np.hstack([ind0, self.data.getFrameIndex('cluster_selected_shot_first_arr', input_file=self.data.web_proofread_cluster)])
                        ind = self.data.getFrameIndex('cluster_selected_arr_'+cmd_out, input_file=self.data.web_proofread_cluster)
                        ind = vutil.removeArr(ind, ind0)
                    # copy images into final folder
                    segs = sorted(glob(fn+'/*.png'))
                    assert len(segs) == len(ind)
                    black_frame = np.loadtxt(self.data.video_stats_black).astype(int)
                    vutil.postprocessSeg(segs, [output_mask_template%x for x in ind], black_frame, self.data.SEG_THRES)
                elif 'STM' in cmd:
                    # STM-cluster-shot_first
                    # STM-folder-1fps
                    cmd_file = 'run_stm_%d_%d.sh' % (job_id, job_num)
                    if vid == 0:
                        if os.path.exists(cmd_file):
                            os.remove(cmd_file)
                        vutil.writetxt(cmd_file, ['#/bin/bash'])
                        os.chmod(cmd_file, 0o755)
                    js_file = self.data.web_proofread_cluster
                    cmd_in = cmd[cmd.find('-')+1:cmd.rfind('-')]
                    cmd_out = cmd[cmd.rfind('-')+1:]
                    stm_mem_step = 1
                    stm_mem_len = 100
                    output_mask_template = os.path.join(self.data.vast_stm.format('_'+cmd_out), self.data.SEG_FMT)
                    input_mask_template = os.path.join(self.data.vast_stm.format('_all'), self.data.SEG_FMT)
                    option_output = 'cluster_selected_'+cmd_out
                    if cmd_in == 'cluster':
                        if cmd_out == 'shot_first': # cluster -> shot_first
                            option_inputs = [option_cluster]
                        elif cmd_out == 'shot_every10': # cluster+shot_first -> every10
                            option_inputs = [option_cluster, 'cluster_selected_shot_first']
                        elif 'fps' in cmd_out: # cluster+shot_first -> every10
                            option_inputs = [cmd_out]
                            output_mask_template = input_mask_template
                        elif cmd_out == 'shot_all': # cluster+shot_first -> every10
                            stm_mem_step = 4
                            option_inputs = [option_cluster, 'cluster_selected_shot_first', 'cluster_selected_shot_every10']
                            output_mask_template = input_mask_template
                    elif cmd_in == 'folder':
                        option_inputs = vutil.extractId(self.data.vast_stm.format('_all')) 
                        option_output = self.data.getFrameIndex(option = 'shot_selected_1fps')
                        
                    input_image_index, output_image_index, output_mask_index = self.data.getSTMIndex(js_file, option_inputs, option_output)
                    if cmd_out == '_all' in cmd_out:
                        output_mask_index = output_image_index
                        stm_mem_step = 5
                    self.processor.segSTM(cmd_file, self.data.video_frame_template, input_image_index, output_image_index, \
                                          input_mask_template, input_image_index, output_mask_template, output_mask_index, stm_mem_step, stm_mem_len)
                    self.proofreader.vastProofreadSeg(vutil.flatList(output_image_index), self.data.frame_size[::-1], self.data.vast_folder, ['im_'+cmd], ['im'])

                elif cmd == 'shot-detection': # for annotation propagation
                    self.processor.shotDetection(self.data.video_frame_template, self.data.video_stats_shot)
                elif 'release' in cmd:
                    if cmd == 'release-seg-shot_all':
                        frame_ids = self.data.getFrameIndex()
                        seg_template = os.path.join(self.data.vast_stm.format('_all'), self.data.SEG_FMT)
                        fn = video_name.replace('/','_')
                        im_template = self.data.release_frame_template
                        output_template = self.data.release_seg_template
                        self.processor.segRefinement(frame_ids, im_template, seg_template, output_template)
                        import pdb; pdb.set_trace()
                elif 'print' in cmd:
                    if cmd == 'print-name':
                        print(video_name)
                    elif cmd == 'print-shot-server':
                        print(self.data.web_proofread_server.format('shot'))
                else:
                    raise Exception('command %s not found.'%cmd)
