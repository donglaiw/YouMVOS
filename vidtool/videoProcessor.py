import os,shutil
import numpy as np
from glob import glob
from skimage.measure import label
from skimage.color import label2rgb
import imageio
from scipy.ndimage import zoom

from . import videoUtil as vutil
from .lib import shotDetection
from .lib import frameCluster

class videoProcessor(object):
    def __init__(self):
        self.redo = False
        self.lib_shot_detection = None
        self.lib_frame_cluster = None
        self.lib_seg_refinement = None
    
    def setLibInfo(self, lib_detectron2, lib_stm):
        self.lib_detectron2 = lib_detectron2
        self.lib_stm = lib_stm
    
    def setRedo(self, redo):
        self.redo = redo

    def setFolderInfo(self, folder_proofread, frame_offset):
        # for all videos
        self.folder_proofread = folder_proofread
        self.frame_offset = frame_offset

    def downloadVideo(self, video_url, video_folder):
        video_file = os.path.join(video_folder, video_url+'.mp4')
        if self.redo or not os.path.exists(video_file):
            print('Downloading:', video_file)
            vutil.downloadVideo(video_url, video_file, 136)
            if not os.path.exists(video_file):
                print('try 480p')
                vutil.downloadVideo(video_url, video_file, 135)
        else:
            print('Existed:', video_file)

    def extractFrames(self, lib_ffmpeg, video_file, frame_template):
        frame_file = frame_template % 1 # index start from 1
        if self.redo or not os.path.exists(frame_file):
            vutil.mkdir(frame_file)
            os.system(lib_ffmpeg + ' -i %s %s' % (video_file, frame_template))
        else:
            print('Exist %s' % frame_file)


    def frameCopy(self, input_template, output_template, frame_ids, frame_downsample = 1):
        vutil.mkdir(output_template, 'parent')
        for frame_id in frame_ids:
            frame_in = input_template % frame_id
            frame_out = output_template % frame_id
            if not os.path.exists(frame_out):
            #tmp = imageio.imread(frame_out)
            #if tmp.shape[0]==88:
                print('do: ',frame_out)
                if frame_downsample != 1:
                    output = imageio.imread(frame_in)[::frame_downsample, ::frame_downsample]
                    imageio.imwrite(frame_out, output)
                else:
                    shutil.copy(frame_in, frame_out)

    def frameDownsample(self, output_template = None, frame_downsample = 4, frame_rate = -1, frame_ids='all', job_id = 0, job_num = 1):
        if output_template is None:
            output_template = self.data.getFrameName(-1, suffix = '_ds')
        if frame_rate < 0 :
            frame_rate = self.data.frame_rate
        if job_id == 0: # avoid multiple thread conflicts
            vutil.mkdir(output_template, 'dir')
        if isinstance(frame_ids, str): 
            frame_ids = self.data.getFrameIndex(frame_ids)

        frame_size = np.array(self.data.getFrameImage(frame_ids[0]).shape)
        frame_size[:2] = (frame_size[:2] + frame_downsample - 1) // frame_downsample
        for frame_id in frame_ids[job_id :: job_num]:
            output_file = self.data.getFrameName(frame_id, output_template)
            if self.data.redo or not os.path.exists(output_file):
                output = self.data.getFrameImage(frame_id)[::frame_downsample, ::frame_downsample]
                imageio.imwrite(output_file, output)

    # 1. shot detection/frame clustering
    def shotDetection(self, frame_template, output_file, thres_dark = 50, thres_diff = 20, thres_shot_len = 1):
        if self.lib_shot_detection is None: # initialization
            self.lib_shot_detection = shotDetection()
        # glob all frames
        if not os.path.exists(output_file):
            self.lib_shot_detection.setFolder(frame_template, output_file)
            # compute rgb diff
            self.lib_shot_detection.computeMaxDiff()
            # compute shot
            self.lib_shot_detection.computeShot(thres_dark, thres_diff, thres_shot_len)
        else:
            print('Exist:', output_file)

    # for frame clustering
    def frameCluster(self, frame_template, frame_ids, output_file, thres_sim = 0.86, thres_small = [5,0.82], metric = 'cosine'):
        if self.lib_frame_cluster is None: # initialization
            self.lib_frame_cluster = frameCluster()
        vutil.mkdir(output_file, 'parent')
        if self.redo or not os.path.exists(output_file):
            frame_names = [frame_template%x for x in frame_ids]
            self.lib_frame_cluster.setInfo(frame_names)
            cluster_ids = self.lib_frame_cluster.getClusterId(thres_sim, thres_small, metric)
            np.savetxt(output_file, cluster_ids, '%d')
    
    def computeBlackFrame(self, frame_template, frame_ids, output_file, thres_black = 5):
        if self.redo or not os.path.exists(output_file):
            vutil.mkdir(output_file, 'parent')

            output = -np.ones([len(frame_ids), 4], int)
            for i,frame_id in enumerate(frame_ids):
                frame_name = frame_template % frame_id
                if os.path.exists(frame_name):
                    tmp = imageio.imread(frame_name).max(axis=2)
                    row_black = np.where(tmp.max(axis=1) > thres_black)[0]
                    if len(row_black)>0:
                        output[i, 0] = row_black[0]
                        output[i, 2] = row_black[-1]
                    col_black = np.where(tmp.max(axis=0) > thres_black)[0]
                    if len(col_black)>0:
                        output[i, 1] = col_black[0]
                        output[i, 3] = col_black[-1]
            output = output[output[:,0]>=0]
            ran = np.hstack([output[:,:2].min(axis=0), output[:,2:].max(axis=0)])
            np.savetxt(output_file, ran, '%d')

    # 2. Detectron2 for 2D instance segmentation
    def segDetectron2(self, frame_ids, image_template, output_template, cmd_file):
        # https://github.com/donglaiw/detectron2
        vutil.mkdir(output_template)

        # pointrend
        cmd = 'python ' + self.lib_detectron2 + 'demo/demo_youtop.py --config-file  ' + self.lib_detectron2 + 'projects/PointRend/configs/InstanceSegmentation/pointrend_rcnn_R_50_FPN_3x_coco.yaml --input-template %s --input-index %s --output %s --opts MODEL.WEIGHTS detectron2://PointRend/InstanceSegmentation/pointrend_rcnn_R_50_FPN_3x_coco/164955410/model_final_3c3198.pkl\n'
        # maskrcnn
        #cmd = 'python ' + self.lib_detectron2 + 'demo/demo_youtop.py --config-file  ' + self.lib_detectron2 + 'configs/COCO-InstanceSegmentation/mask_rcnn_R_50_FPN_3x.yaml --input-template %s --input-index %s --output %s --opts MODEL.WEIGHTS detectron2://COCO-InstanceSegmentation/mask_rcnn_R_50_FPN_3x/137849600/model_final_f10217.pkl\n'
        frame_ids_str = ','.join([str(x) for x in frame_ids])
        cmd = cmd % (image_template, frame_ids_str, output_template)
        if cmd_file is None:
            print(cmd)
        else:
            vutil.writetxt(cmd_file, cmd, 'a')

    # 3. STM for video object segmentation
    def segSTM(self, cmd_file, input_image_template, input_image_index, output_image_index,\
                input_mask_template, input_mask_index, output_mask_template, output_mask_index, \
                stm_mem_step=1, stm_mem_len = 100):
        # option 1: each mask is the first index in the frame_ids 
        # option 2: each mask index is a downsample version of frame_ids 
        # https://github.com/donglaiw/STM

        input_mask_index_str = vutil.convertClusterListToStr(input_mask_index)
        output_mask_index_str = vutil.convertClusterListToStr(output_mask_index)
        input_image_index_str = vutil.convertClusterListToStr(input_image_index)
        output_image_index_str = vutil.convertClusterListToStr(output_image_index)

        vutil.mkdir(output_mask_template, 'parent')

        cmd = 'python ' + self.lib_stm + 'demo_youtop.py --image-template %s --image-input-index "%s" --image-output-index "%s" --mask-template-input %s --mask-input-index "%s" --mask-template-output %s --mask-output-index "%s" --stm-height 480 --stm-mem-step %d --stm-mem-len %d --redo %d\n'
        cmd = cmd % (input_image_template, input_image_index_str, output_image_index_str,\
                     input_mask_template, input_mask_index_str, output_mask_template, output_mask_index_str, stm_mem_step, stm_mem_len, self.redo)
        if cmd_file is None:
            print(cmd)
        else:
            vutil.writetxt(cmd_file, cmd, 'a')

    # grabcut for refinement
    def segRefinement(self, frame_ids, im_template, seg_template, output_template,\
                     mask_id_func=None, valid_ran=None):
        from .lib import segRefinement
        if self.lib_seg_refinement is None:
            self.lib_seg_refinement = segRefinement() 
        
        im_size = imageio.imread(im_template % frame_ids[0]).shape
        black = np.zeros(im_size[:2], np.uint8)
        vutil.mkdir(output_template, 'parent')
        for frame_id in frame_ids:
            output_name = output_template % frame_id
            # check invalid
            redo = self.redo
            if not os.path.exists(output_name):
                redo = True
            else:
                try:
                    im = imageio.imread(output_name)
                except:
                    print("can't read", output_name)
                    redo = True

            if redo :
            #if self.data.redo or not os.path.exists(output_name):
                im_name = im_template % frame_id
                if mask_id_func is None:
                    seg_name = seg_template % frame_id
                else:
                    seg_name = seg_template % mask_id_func(frame_id)
                if os.path.exists(seg_name): 
                    seg = imageio.imread(seg_name)
                    if valid_ran is not None:
                        # add 1-pix border
                        seg[:valid_ran[0]+1] = 0
                        seg[valid_ran[2]:] = 0
                        seg[:, :valid_ran[1]+1] = 0
                        seg[:, valid_ran[3]:] = 0
                    im = imageio.imread(im_name)
                    seg_out = self.lib_seg_refinement.segRefineGrabcut(im, seg)
                    if seg_out is not None:
                        imageio.imwrite(output_name, seg_out)    
                else:
                    imageio.imwrite(output_name, black)
