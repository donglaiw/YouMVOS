import os,shutil
import numpy as np
from glob import glob
from skimage.measure import label
from skimage.color import label2rgb
import imageio
from scipy.ndimage import zoom

from .videoBasic import videoBasic
from . import videoUtil as vutil

class videoProcessor(videoBasic):
    def __init__(self, job_id = 0, job_num = 1, redo = False):
        super().__init__(job_id, job_num, redo)

    # 1. Shot detection
    def getStat(self, stat, stat_folder = None):
        if stat_folder is None:
            stat_folder = self.video_data_folder
        stat_path = stat_folder + ('%s.txt'%stat)
        if not os.path.exists(stat_path):
            raise ValueError('File does not exist: ', stat_path)
        return np.loadtxt(stat_path).astype(int)

    def computeMaxDiff(self, frame_downsample=4):
        if self.job_num != 1: # for long movies
            output_path_max = self.video_data_folder + 'rgb_max/'
            output_path_diff = self.video_data_folder + 'rgb_diff/'
            if self.job_id == 0: # avoid multiple thread conflicts
                U_mkdir(output_path_max)
                U_mkdir(output_path_diff)
            output_file_max = output_path_max + '%d_%d.txt'%(self.job_id, self.job_num)
            output_file_diff = output_path_diff + '%d_%d.txt'%(self.job_id, self.job_num)
        else: # for short videos
            output_file_max = self.video_data_folder+'rgb_max.txt'
            output_file_diff = self.video_data_folder+'rgb_diff.txt'

        do_max = not os.path.exists(output_file_max)
        do_diff = not os.path.exists(output_file_diff)
        if do_max or do_diff:
            print('compute max/diff')
            # not using the last frame
            frame_range = self.getKeyframeIndex(-1, frame_rate = 1)[:-1] 
            output_diff = np.zeros(len(frame_range), int)
            # if last job
            if frame_range[-1] == self.video_frame_num-2:
                output_max = np.zeros(len(frame_range)+1, int)
            else:
                output_max = np.zeros(len(frame_range), int)
            frame_current = self.getFrame(frame_range[0])[::frame_downsample, ::frame_downsample].astype(float)

            for i, frame_id in enumerate(frame_range):
                output_max[i] = frame_current.max()
                frame_next = self.getFrame(frame_id+1)[::frame_downsample, ::frame_downsample].astype(float)
                output_diff[i] = np.abs(frame_current - frame_next).mean()
                frame_current[:] = frame_next

            if frame_range[-1] == self.video_frame_num-2:
                output_max[-1] = frame_next.max()

            np.savetxt(output_file_max, output_max, '%d')
            np.savetxt(output_file_diff, output_diff, '%d')

    def computeMaxDiffCombine(self):
        for name in ['rgb_diff', 'rgb_max']:
            output_path = self.output_folder+name
            output_file = output_path+'.txt'
            if not os.path.exists(output_file):
                result_file = glob(output_path+'/*.txt')
                num_result = len(result_file)
                if num_result == 0:
                    raise ValueError('Empty Folder: ',output_path)
                else:
                    _, job_num = result_file[0][result_file[0].rfind('/')+1:result_file[0].find('.')].split('_')
                    job_num = int(job_num) 
                    if job_num != num_result:
                       raise ValueError('Missing %d Files'%(job_num-num_result))
                    else:
                        output_len = self.frame_num
                        if name == 'rgb_diff':
                            output_len = self.frame_num - 1
                        output = np.zeros(output_len, int)
                        start_id = 0
                        for job_id in range(job_num):
                            result = np.loadtxt(output_path+'/%d_%d.txt'%(job_id,job_num)).astype(int)
                            output[start_id:start_id+len(result)] = result
                            start_id += len(result)
                    np.savetxt(output_file, output, '%d')

    def computeShot(self, threshold_dark = 20, threshold_diff = 10, threshold_shot_len = 12):
        # ideal: 0s surround the peak
        # if not sure, connect things
        # also remove small shots
        
        if threshold_shot_len == 0:
            raise ValueError('threshold_shot_len must be bigger than 0')

        output_path = self.video_data_folder+'shot.txt'
        if not os.path.exists(output_path):
            rgb_max = self.getStat('rgb_max')
            rgb_diff = self.getStat('rgb_diff')
            
            # Break the video by dark frames.
            frame_chunk = label(rgb_max >= threshold_dark)
            _, chunk_len = np.unique(frame_chunk, return_counts = True)
            # If all 0s
            if len(chunk_len) == 1:
                chunk_len = np.hstack([0,chunk_len])
                frame_chunk[:] = 1 
            num_chunk = frame_chunk.max()
            output = [None]*num_chunk
            for chunk_id in range(num_chunk):
                frame_id = np.where(frame_chunk == chunk_id + 1)[0]
                print('%d: %d-%d' % (chunk_id, frame_id[0], frame_id[-1]))
                if chunk_len[chunk_id + 1] > 2 * threshold_shot_len:
                    # Find initial change points by diff threshold
                    rgb_diff_chunk = rgb_diff[frame_id[0]:frame_id[-1]+1]
                    frame_change = np.where(rgb_diff_chunk[threshold_shot_len:-threshold_shot_len] >= threshold_diff)[0]+threshold_shot_len 

                    # Select change points with enough shot length (no other change points nearby)
                    frame_nearby = frame_change + np.arange(-threshold_shot_len, threshold_shot_len+1).reshape([-1,1])
                    frame_change_v2 = np.array([-1] \
                                   + list(frame_change[(rgb_diff_chunk[frame_nearby] >= threshold_diff).sum(axis=0)==1]) \
                                   + [len(rgb_diff_chunk)-1])

                    # remove dark frames
                    output[chunk_id] = frame_id[0]+np.vstack([frame_change_v2[:-1]+1, frame_change_v2[1:]]).T
                else:
                    output[chunk_id] = [frame_id[0], frame_id[-1]]
            
            np.savetxt(output_path, np.vstack(output), '%d')

    # 2. Detectron2 for 2D instance segmentation
    def computeDetectron2Seg(self, detectron2_folder, frame_index = 0, \
                             image_folder = None, output_folder = None, \
                             shot_file = None, cmd_file = None):
        # https://github.com/donglaiw/detectron2
        frame_index = self.getKeyframeIndex(frame_index, shot_file)
        frame_index += 1 # ffmpeg

        if image_folder is None:
            image_folder = self.getFrameName(-1)
        if output_folder is None:
            output_folder =  self.video_share_folder + 'seg/'
        vutil.mkdir(output_folder)

        # pointrend
        cmd = 'python ' + detectron2_folder + 'demo/demo_youtop.py --config-file  ' + detectron2_folder + 'projects/PointRend/configs/InstanceSegmentation/pointrend_rcnn_R_50_FPN_3x_coco.yaml --input-template %s --input-index %s --output %s --opts MODEL.WEIGHTS detectron2://PointRend/InstanceSegmentation/pointrend_rcnn_R_50_FPN_3x_coco/164955410/model_final_3c3198.pkl\n'
        # maskrcnn
        #cmd = 'python ' + detectron2_folder + 'demo/demo_youtop.py --config-file  ' + detectron2_folder + 'configs/COCO-InstanceSegmentation/mask_rcnn_R_50_FPN_3x.yaml --input-template %s --input-index %s --output %s --opts MODEL.WEIGHTS detectron2://COCO-InstanceSegmentation/mask_rcnn_R_50_FPN_3x/137849600/model_final_f10217.pkl\n'
        frame_index_str = ','.join([str(x) for x in frame_index])
        cmd = cmd % (image_folder, frame_index_str, output_folder + 'seg_%05d.png')
        if cmd_file is None:
            print(cmd)
        else:
            vutil.writetxt(cmd_file, cmd, 'a')

    # 3. STM for video object segmentation
    def computeSTMSeg(self, STM_folder, index_type = 'shot_all_list', index_file = None, frame_index = None, \
                             image_template = None, mask_folder = None, output_folder = None, \
                             cmd_file = None, redo = 0):
        # https://github.com/donglaiw/STM
        # frame_index: list of arrays (cluster result) or Nx2 matrix (shot result)  


        if index_type == 'shot_all_list':
            if frame_index is None: 
                frame_index = self.getKeyframeIndex(index_type, index_file, frame_offset = 1)
            frame_index_str = vutil.convertClusterListToStr(frame_index)
        elif index_type == 'cluster':
            frame_index_str = self.loadClusterJs(cluster_js, 'selected_str')
        else:
            raise ValueError('unknown index_type: %s' % index_type)

        if image_template is None:
            image_template = self.getFrameName(-1)
        if mask_folder is None:
            mask_folder =  self.video_share_folder % '' + 'seg_shot_bd/'
        masks = glob(mask_folder + '/*.png')
        if len(masks) == 0:
            print("%s has no mask to run." % mask_folder)
            return
        if output_folder is None:
            output_folder =  self.video_share_folder % '' + 'seg_prop/'
        vutil.mkdir(output_folder)
        # sample rate: need to be divisible
        if self.video_frame_rate in [25,30]:
            image_step = self.video_frame_rate // 5
        elif self.video_frame_rate in [24]:
            image_step = self.video_frame_rate // 6
        else:
            raise ValueError('unsuitable video frame rate for propagation: %d' % image_step)
        cmd = 'python ' + STM_folder + 'demo_youtop.py --image-template %s  --mask-folder %s --output-template %s --input-index "%s" --input-fps %d --image-step %d --stm-height 480 --shot-chunk-len 500 --redo %d\n'
        cmd = cmd % (image_template, mask_folder, output_folder + 'seg_%05d.png', frame_index_str, self.video_frame_rate, image_step, redo)
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
