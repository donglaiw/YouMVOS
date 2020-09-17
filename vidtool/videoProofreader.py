import os,sys
import math
import numpy as np
from glob import glob
import imageio

from .views import *

from .videoBasic import videoBasic
from . import videoUtil as vutil

class videoProofreader(videoBasic):
    def __init__(self, job_id = 0, job_num = 1, redo = False):
        super().__init__(job_id, job_num, redo)
    
    def webProofreadFolder(self):
        folder_name = (self.video_web_folder % 'proofread/')[:-1]
        folder_name = folder_name[:folder_name.rfind('/') + 1]
        if not os.path.exists(folder_name + '/saved/'):
            os.mkdir(folder_name + '/saved/')
            os.chmod(folder_name + '/saved/', 0o777)
        vutil.mkdir(folder_name + '/test/')
        vutil.mkdir(folder_name + '/result/')

    def webProofreadShot(self, input_txt = None, output_folder = None, frame_rate = -1):
        # Convert shot_txt into js and html
        if frame_rate < 0 :
            frame_rate = self.video_frame_rate

        output_js = self.getJs(output_folder, '_shot')
        if self.redo or not os.path.exists(output_js):
            print('do js')
            import pdb; pdb.set_trace()
            input_file = self.getTxt(input_txt, 'shot')
            shots = np.loadtxt(input_file).astype(int)
            output_var = self.convertShotArrToJs(shots, frame_rate)
            vutil.writetxt(output_js, output_var)

        output_html = self.getHtml(output_folder, '_shot')
        if self.redo or not os.path.exists(output_html):
            print('do shot')
            output = html_shot % ('../../../frame_ds/', self.video_name, (self.video_frame_num + self.video_frame_rate - 1) // self.video_frame_rate, self.video_frame_rate)
            vutil.writetxt(output_html, output)

    def webProofreadCluster(self, input_txt = None, output_folder = None, frame_rate = -1):
        # Convert shot_txt into js and html
        if frame_rate < 0 :
            frame_rate = self.video_frame_rate

        output_js = self.getJs(output_folder, '_cluster')
        if self.redo or not os.path.exists(output_js):
            print('do js')
            input_file = self.getTxt(input_txt, 'cluster')
            if os.path.exists(input_file):
                shots = np.loadtxt(input_file).astype(int)
            else: # default 1 cluster
                shots = [self.getKeyframeIndex()]
            output_var = self.convertClusterListToJs(shots)
            vutil.writetxt(output_js, output_var)

        output_html = self.getHtml(output_folder, '_cluster')
        if self.redo or not os.path.exists(output_html):
            print('do cluster')
            output = html_cluster % ('../../../frame_ds/', self.video_name, (self.video_frame_num + self.video_frame_rate - 1) // self.video_frame_rate)
            vutil.writetxt(output_html, output)

    def webProofreadSeg(self, input_txt = None, output_folder = None, frame_rate = -1):
        # Convert shot_txt into js and html
        if frame_rate < 0 :
            frame_rate = self.video_frame_rate

        output_html = self.getHtml(output_folder, '_seg')
        if self.redo or not os.path.exists(output_html):
            print('do seg')
            overlay_files = sorted(glob(output_html[:output_html.rfind('/')] + '/../../../seg_ds/'+self.video_name+'/*.png'))
            overlay_id = ','.join([str(int(x[x.rfind('_')+1:-4])) for x in overlay_files]) 
            output = html_seg % ('../../../frame_ds/', '../../../seg_ds/', self.video_name, overlay_id, (self.video_frame_num + self.video_frame_rate - 1) // self.video_frame_rate, self.video_frame_rate)
            vutil.writetxt(output_html, output)

    def vastProofreadSeg(self, frame_index = 0, frame_suf=None, shot_js = None, output_folder = None):
        # Output im.vsvi and seg.vsvi for VAST-lite proofreading
        if frame_suf is None:
            frame_suf = self.getKeyframeSuf(frame_index)
        if isinstance(frame_index, int):
            # frame_index is the option
            frame_index = self.getKeyframeIndex(frame_index, shot_js)

        # ffmpeg starts from id=1
        frame_index_str = ','.join([str(1 + x) for x in frame_index])
        frame_size = np.array(self.getFrame(0).shape)

        if output_folder is None:
            output_folder = self.video_share_folder

        # output vsvi
        vsvi_type = ['im', 'seg']
        vsvi_filename = ['image_%05d.png','seg_%05d.png']
        for vsvi_id in range(len(vsvi_type)):
            output_vsvi = output_folder + '%s.vsvi' % (vsvi_type[vsvi_id] + frame_suf)
            if self.redo or not os.path.exists(output_vsvi):
                meta = "%s %s" % (self.video_name, vsvi_type[vsvi_id])
                image_template = r'.\%s\%s' % (vsvi_type[vsvi_id], vsvi_filename[vsvi_id])
                output = vsvi_seg % (meta, image_template, 0, \
                                                   image_template, frame_size[1], frame_size[0], \
                                                   frame_index_str, frame_size[1], frame_size[0], \
                                                   len(frame_index), meta)
                vutil.writetxt(output_vsvi, output)

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
            
