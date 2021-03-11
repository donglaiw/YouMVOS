import os,shutil
import numpy as np
from glob import glob
from skimage.measure import label
from skimage.color import label2rgb
import imageio
from scipy.ndimage import zoom

from .. import videoUtil as vutil

class videoProcessor(object):
    def __init__(self, data):
        self.data = data
        self.lib_shot_detection = None
        self.lib_seg_refinement = None
        self.lib_frame_cluster = None
        self.job_id = 0
        self.job_num = 1

    # 0. frame i/o
    def frameSize(self):
        im = imageio.imread(self.data.getFrameName(1))
        return im.shape

    def frameCopy(self, output_folder, frame_ids='all', frame_rate = -1, frame_downsample = 1):
        vutil.mkdir(output_folder)
        if frame_rate < 0:
            frame_rate = self.data.video_frame_rate
        if isinstance(frame_ids, str): 
            frame_ids = self.data.getFrameIndex(frame_ids, frame_rate)

        for frame_id in frame_ids[self.job_id :: self.job_num]:
            frame_name_in = self.data.getFrameName(frame_id)
            frame_name_out = output_folder % frame_id
            if self.data.redo or not os.path.exists(frame_name_out):
                print('do: ',frame_name_out)
                if frame_downsample != 1:
                    output = imageio.imread(frame_name_in)[::frame_downsample, ::frame_downsample]
                    imageio.imwrite(frame_name_out, output)
                else:
                    shutil.copy(frame_name_in, frame_name_out)

    def frameDownsample(self, output_template = None, frame_downsample = 4, frame_rate = -1, frame_ids='all', job_id = 0, job_num = 1):
        if output_template is None:
            output_template = self.data.getFrameName(-1, suffix = '_ds')
        if frame_rate < 0 :
            frame_rate = self.data.video_frame_rate
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
    # for shot youtube clips
    def shotDetection(self, thres_dark = 50, thres_diff = 20, thres_shot_len = 1):
        from ..lib import shotDetection
        frame_folder = self.data.FOLDER_DOWNLOAD.format(self.data.video_name)
        if self.lib_shot_detection is None:
            self.lib_shot_detection = shotDetection(frame_folder)
        else:
            self.lib_shot_detection.setFolder(frame_folder)
        # compute rgb diff
        self.lib_shot_detection.computeMaxDiff()
        # compute shot
        self.lib_shot_detection.computeShot(thres_dark, thres_diff, thres_shot_len)

    # for frame clustering
    def frameCluster(self, frame_template = None, thres_sim = 0.86, thres_small = [5,0.82], metric = 'cosine'):
        from ..lib import frameCluster
        if frame_template is None:
            frame_template = self.data.FRAME_NAME.format(self.data.video_name, '_ds')

        output_file = self.data.getJs(suf = '_cluster')
        vutil.mkdir(output_file, 'dir')
        if self.data.redo or not os.path.exists(output_file):
            frame_ids = self.data.getFrameIndex()
            frame_names = [frame_template%x for x in self.data.getFrameIndex()]
            if self.lib_frame_cluster is None:
                self.lib_frame_cluster = frameCluster(frame_names, self.data.video_frame_rate)
            else:
                self.lib_frame_cluster.setInfo(frame_names, self.data.video_frame_rate)
            cluster_ids = self.lib_frame_cluster.getClusterId(thres_sim, thres_small, metric)
            vutil.writetxt(output_file, vutil.convertClusterToJs(cluster_ids))
    
    def computeBlackFrame(self, frame_num = 30, thres_black = 5, frame_folder = None, output_file = None):
        if frame_folder is None:
            frame_folder = self.data.getFrameName(-2)
        if output_file is None:
            output_file = self.data.FOLDER_DOWNLOAD + self.data.video_name + '/black_frame%d.txt'%thres_black

        if self.data.redo or not os.path.exists(output_file):
            vutil.mkdir(output_file, 'dir')
            frame_ids = self.data.getFrameIndex('uniform', frame_num = frame_num)

            output = -np.ones([len(frame_ids), 4], int)
            for i,frame_id in enumerate(frame_ids):
                frame_name = self.data.FRAME_NAME.format(self.data.video_name, '') % frame_id
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
    def segDetectron2(self, frame_ids = 'shot', \
                             image_template = None, output_template = None, \
                             input_file = None, cmd_file = None):
        # https://github.com/donglaiw/detectron2
        detectron2_folder = self.data.LIB_DETECTRON2
        if isinstance(frame_ids, str):
            frame_ids = self.data.getFrameIndex(frame_ids, input_file = input_file)
        if image_template is None:
            image_template = self.data.getFrameName(-1)
        if output_template is None:
            output_template =  self.data.PROCESSOR_DETECTON2.format(self.data.video_name)
        vutil.mkdir(output_template, 'dir')

        # pointrend
        cmd = 'python ' + detectron2_folder + 'demo/demo_youtop.py --config-file  ' + detectron2_folder + 'projects/PointRend/configs/InstanceSegmentation/pointrend_rcnn_R_50_FPN_3x_coco.yaml --input-template %s --input-index %s --output %s --opts MODEL.WEIGHTS detectron2://PointRend/InstanceSegmentation/pointrend_rcnn_R_50_FPN_3x_coco/164955410/model_final_3c3198.pkl\n'
        # maskrcnn
        #cmd = 'python ' + detectron2_folder + 'demo/demo_youtop.py --config-file  ' + detectron2_folder + 'configs/COCO-InstanceSegmentation/mask_rcnn_R_50_FPN_3x.yaml --input-template %s --input-index %s --output %s --opts MODEL.WEIGHTS detectron2://COCO-InstanceSegmentation/mask_rcnn_R_50_FPN_3x/137849600/model_final_f10217.pkl\n'
        frame_ids_str = ','.join([str(x) for x in frame_ids])
        cmd = cmd % (image_template, frame_ids_str, output_template)
        if cmd_file is None:
            print(cmd)
        else:
            vutil.writetxt(cmd_file, cmd, 'a')

    # 3. STM for video object segmentation
    def segSTM(self, frame_ids = 'shot_all_list', frame_ids_file = None, frame_ids_after = -1, \
                             image_template = None, mask_folder = None, mask_index_factor = -1, output_template = None, \
                             cmd_file = None, mask_step_input = 0, mask_step_input_offset = -1, mask_step_output = -1, \
                             stm_anchor_num = -1, stm_len =150, stm_step = -1):
        # option 1: each mask is the first index in the frame_ids 
        # option 2: each mask index is a downsample version of frame_ids 
        # https://github.com/donglaiw/STM
        # frame_ids: list of arrays (cluster result) or Nx2 matrix (shot result)  
        # mask_folder: can have different indexing system (so long it's indexed)

        STM_folder = self.data.LIB_STM
        # sample rate: need to be divisible
        if stm_step < 0 :
            stm_step = self.data.video_frame_step
        if mask_step_input_offset < 0:
            mask_step_input_offset = self.data.FRAME_OFFSET
        if isinstance(frame_ids, str):
            option = frame_ids
            if '_out' in option: # 6FPS
                if 'shot' in option:
                    frame_ids = self.data.getFrameIndex(option, input_file = '_shot_out', frame_rate = stm_step)
                elif 'cluster' in frame_ids:
                    frame_ids = self.data.loadClusterJs(option=option)
                else:
                    raise ValueError('unknown frame_ids: %s' % frame_ids)
                # input mask step
                if mask_step_input == 0:
                    mask_step_input = self.data.video_frame_rate
                # prop per frame_step
                if mask_step_output < 0:
                    mask_step_output = self.data.video_frame_step
            else:
                # prop per sec
                if mask_step_output < 0:
                    mask_step_output = self.data.video_frame_rate
                if 'shot' in option:
                    frame_ids = self.data.getFrameIndex(option, input_file = frame_ids_file)
                elif 'cluster' in frame_ids:
                    frame_ids = self.data.loadClusterJs(option=option)
                else:
                    raise ValueError('unknown frame_ids: %s' % frame_ids)
        if frame_ids_after > 0:
            for i in range(len(frame_ids)):
                frame_ids[i] = [x for x in frame_ids[i] if x > frame_ids_after]
            frame_ids = [x for x in frame_ids if len(x) > 0]
        frame_ids_str = vutil.convertClusterListToStr(frame_ids)
        if image_template is None:
            image_template = self.data.getFrameName(-1)
        if mask_folder is None:
            mask_folder =  self.data.FOLDER_VAST.format(self.data.video_name) + 'seg_shot_bd/'
        if output_template is None:
            output_template =  self.data.PROCESSOR_STM.format(self.data.video_name)

        masks = glob(mask_folder + '/*.png')
        if len(masks) == 0:
            print("%s has no mask to run." % mask_folder)
            #return
        vutil.mkdir(output_template, 'dir')

        # mode=shot: first frame is labeled, while others are to be propagated
        # mode=index: need mask to have the index

        cmd = 'python ' + STM_folder + 'demo_youtop.py --video-fps %d --image-template %s --image-cluster "%s" --mask-folder %s --mask-index-factor %d,%d --mask-index-factor-output %d,%d --mask-template-output %s --stm-step %d --stm-height 480 --stm-mem-len %d --stm-anchor-num %d --redo %d\n'
        cmd = cmd % (self.data.video_frame_rate, image_template, frame_ids_str, mask_folder, mask_step_input, mask_step_input_offset, mask_step_output, self.data.FRAME_OFFSET, output_template, stm_step, stm_len, stm_anchor_num, self.data.redo)
        if cmd_file is None:
            print(cmd)
        else:
            vutil.writetxt(cmd_file, cmd, 'a')

    # grabcut for refinement
    def segRefinement(self, im_folder = None, seg_folder = None, output_folder = None,\
                      frame_step = -1, iter_image = 30, iter_algo = 50, mask_id_func=None, valid_ran=None):
        from ..lib import segRefinement
        if self.lib_seg_refinement is None:
            self.lib_seg_refinement = segRefinement() 
        
        fn = self.data.video_name.replace('/','_')
        if im_folder is None:
            im_folder = self.data.FOLDER_RELEASE + 'JPEGImages/' + fn  + '/%05d.jpg'
        if seg_folder is None:
            seg_folder = self.data.PROCESSOR_STM2.format(self.data.video_name)
        if output_folder is None:
            output_folder = self.data.FOLDER_RELEASE + 'Annotations/' + fn  + '/%05d.png'
        if frame_step == -1:
            frame_step = self.data.video_frame_step

        frame_ids = self.data.getFrameIndex('all', frame_rate=frame_step)
        black = np.zeros(self.data.video_frame_size[::-1], np.uint8)
        for frame_id in frame_ids[self.data.job_id::self.data.job_num]:
            output_name = output_folder % frame_id
            # check invalid
            redo = self.data.redo or not os.path.exists(output_name)
            try:
                im = imageio.imread(output_name)
            except:
                print("can't read", output_name)
                redo = True

            if redo :
            #if self.data.redo or not os.path.exists(output_name):
                im_name = im_folder % frame_id
                if mask_id_func is None:
                    seg_name = seg_folder % frame_id
                else:
                    seg_name = seg_folder % mask_id_func(frame_id)
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
