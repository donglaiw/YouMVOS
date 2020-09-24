import os,shutil
import numpy as np
from glob import glob
from skimage.measure import label
from skimage.color import label2rgb
import imageio
from scipy.ndimage import zoom

from .. import videoUtil as vutil
from ..lib import shotDetection

class videoProcessor(object):
    def __init__(self, data):
        self.data = data
    
    # 0. frame i/o
    def frameCopy(self, output_folder, frame_ids='all', frame_rate = -1, frame_downsample = 1):
        vutil.mkdir(output_folder)
        if frame_rate < 0:
            frame_rate = self.data.video_frame_rate
            if isinstance(frame_ids, str): 
                frame_ids = self.data.getFrameIndex(frame_ids)

        for frame_id in frame_ids[self.job_id :: self.job_num]:
            frame_name_in = self.data.getFrameName(frame_id)
            frame_name_out = output_folder + frame_name_in[frame_name_in.rfind('/'):]
            if not os.path.exists(frame_name_out):
                if frame_downsample != 1:
                    output = imageio.imread(frame_name_in)[::frame_downsample, ::frame_downsample]
                    imageio.imwrite(frame_name_out, output)
                else:
                    shutil.copy(frame_name_in, frame_name_out)

    def frameDownsample(self, output_folder = None, frame_downsample = 4, frame_rate = -1):
        if output_folder is None:
            output_folder = self.data.getFrameName(-2, suffix = '_ds')
        if frame_rate < 0 :
            frame_rate = self.data.video_frame_rate
        if self.job_id == 0: # avoid multiple thread conflicts
            vutil.mkdir(output_folder)
            if isinstance(frame_ids, str): 
                frame_ids = self.data.getFrameIndex(frame_ids)

        frame_size = np.array(self.data.getFrame(0).shape)
        frame_size[:2] = (frame_size[:2] + frame_downsample - 1) // frame_downsample
        for frame_id in frame_ids[self.job_id :: self.job_num]:
            output_file = self.data.getFrameName(frame_id, output_folder)
            if not os.path.exists(output_file):
                output = self.data.getFrame(frame_id)[::frame_downsample, ::frame_downsample]
                imageio.imwrite(output_file, output)
    # 1. shot detection
    # for shot youtube clips
    def shotDetection(self, thres_dark = 50, thres_diff = 20, thres_shot_len = 1):
        video_shot = shotDectection(self.data.video_data_folder)
        # compute rgb diff
        video_shot.computeMaxDiff()
        # compute shot
        video_shot.computeShot(thres_dark, thres_diff, thres_shot_len)

            
            
    # 2. Detectron2 for 2D instance segmentation
    def segDetectron2(self, detectron2_folder=None, frame_ids = 'shot', \
                             image_template = None, output_folder = None, \
                             frame_ids_file = None, cmd_file = None):
        # https://github.com/donglaiw/detectron2
        if detectron2_folder is None:
            detectron2_folder = self.data.lib_detectron2
        if isinstance(frame_ids, str):
            frame_ids = self.data.getFrameIndex(frame_ids, frame_ids_file)
        if image_folder is None:
            image_folder = self.data.getFrameName(-2)
        if output_folder is None:
            output_folder =  self.data.video_share_folder + 'seg/'
        vutil.mkdir(output_folder)

        # pointrend
        cmd = 'python ' + detectron2_folder + 'demo/demo_youtop.py --config-file  ' + detectron2_folder + 'projects/PointRend/configs/InstanceSegmentation/pointrend_rcnn_R_50_FPN_3x_coco.yaml --input-template %s --input-index %s --output %s --opts MODEL.WEIGHTS detectron2://PointRend/InstanceSegmentation/pointrend_rcnn_R_50_FPN_3x_coco/164955410/model_final_3c3198.pkl\n'
        # maskrcnn
        #cmd = 'python ' + detectron2_folder + 'demo/demo_youtop.py --config-file  ' + detectron2_folder + 'configs/COCO-InstanceSegmentation/mask_rcnn_R_50_FPN_3x.yaml --input-template %s --input-index %s --output %s --opts MODEL.WEIGHTS detectron2://COCO-InstanceSegmentation/mask_rcnn_R_50_FPN_3x/137849600/model_final_f10217.pkl\n'
        frame_ids_str = ','.join([str(x) for x in frame_ids])
        cmd = cmd % (image_template, frame_ids_str, output_folder + 'seg_%05d.png')
        if cmd_file is None:
            print(cmd)
        else:
            vutil.writetxt(cmd_file, cmd, 'a')

    # 3. STM for video object segmentation
    def segSTM(self, STM_folder = None, frame_ids = 'shot_all_list', frame_ids_file = None, \
                             image_template = None, mask_folder = None, output_template = None, \
                             cmd_file = None, redo = 0):
        # https://github.com/donglaiw/STM
        # frame_ids: list of arrays (cluster result) or Nx2 matrix (shot result)  
        # mask_folder: can have different indexing system (so long it's indexed)

        if STM_folder is None:
            STM_folder = self.data.LIB_STM
        if isinstance(frame_ids, str):
            if frame_ids == 'shot_all_list':
                frame_ids = self.data.getFrameIndex(frame_ids, input_file = frame_ids_file)
                frame_ids_str = vutil.convertClusterListToStr(frame_ids)
            elif frame_ids == 'cluster':
                frame_ids_str = self.loadClusterJs(cluster_js, 'selected_str')
            else:
                raise ValueError('unknown frame_ids: %s' % frame_ids)

        if image_template is None:
            image_template = self.data.getFrameName(-1)
        if mask_folder is None:
            mask_folder =  self.data.PROCESSOR_VAST_BD % self.data.video_name
        if output_template is None:
            output_template =  self.data.PROCESSOR_STM.format(self.data.video_name)


        masks = glob(mask_folder + '/*.png')
        if len(masks) == 0:
            print("%s has no mask to run." % mask_folder)
            return
        vutil.mkdir(output_template, 'dir')
        # sample rate: need to be divisible
        if self.data.video_frame_rate in [25,30]:
            image_step = self.data.video_frame_rate // 5
        elif self.data.video_frame_rate in [24]:
            image_step = self.data.video_frame_rate // 6
        else:
            raise ValueError('unsuitable video frame rate for propagation: %d' % image_step)

        cmd = 'python ' + STM_folder + 'demo_youtop.py --image-template %s  --mask-folder %s --output-template %s --input-index "%s" --input-fps %d --image-step %d --stm-height 480 --shot-chunk-len 250 --redo %d\n'
        cmd = cmd % (image_template, mask_folder, output_template, frame_ids_str, self.data.video_frame_rate, image_step, redo)
        if cmd_file is None:
            print(cmd)
        else:
            vutil.writetxt(cmd_file, cmd, 'a')

    # grabcut for refinement
    def RefineSeg(self, seg_folder = 'seg_out_all/', seg_folder_path = None,
                 iter_image = 30, iter_algo = 50):
        if seg_folder_path is None:
            seg_folder_path = self.video_share_folder

        refine_folder =  seg_folder_path + seg_folder[:-1] + '_refine/' 
        vutil.mkdir(refine_folder)
        im_folder =  seg_folder_path + 'im/' 
        seg_folder = seg_folder_path + seg_folder 

        files_name_seg = sorted(glob(seg_folder + '*.png'))
        files_name_im = sorted(glob(im_folder + '*.png'))
        for file_name in files_name_seg:
            output_name = refine_folder + file_name[file_name.rfind('/'):]
            if not os.path.exists(output_name):
                seg = imageio.imread(file_name)
                fid = int(file_name[file_name.rfind('s')+1:-4])
                im = imageio.imread(files_name_im[fid])
                seg_out = vutil.segRefineGrabcut(im, seg, iter_image, iter_algo)
                if seg_out is not None:
                    imageio.imwrite(output_name, seg_out)    
