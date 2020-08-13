import os,sys
import math
import numpy as np
from glob import glob

from .views import html_proofread_shot
from .views import vsvi_proofread_seg

from .videoBasic import videoBasic
from . import videoUtil as vutil

class videoProofreader(videoBasic):
    def __init__(self, job_id = 0, job_num = 1, redo = False):
        super().__init__(job_id, job_num, redo)
    

    def webProofreadShot(self, input_shot_txt = None, output_shot_folder = None, frame_rate = -1):
        # Convert shot_txt into js and html
        if frame_rate < 0 :
            frame_rate = self.video_frame_rate

        output_shot_js = self.getShotJs(output_shot_folder)
        if self.redo or not os.path.exists(output_shot_js):
            input_shot_file = self.getShotTxt(input_shot_txt)
            shots = np.loadtxt(input_shot_file).astype(int)
            # Take the ceil for the start frame.
            # Can be repeated due to frame_rate downsample
            shots = np.unique((shots[:, 0] + frame_rate - 1) // frame_rate)
            output_var = 'var shot_start_str="'+','.join([str(x) for x in shots])+'";'
            output_var += 'var shot_selection_str="'+','.join([str(0) for x in shots])+'";'
            vutil.writetxt(output_shot_js, output_var)

        output_shot_html = self.getShotHtml(output_shot_folder)
        if self.redo or not os.path.exists(output_shot_html):
            output = html_proofread_shot % (self.video_name, (self.frame_num + self.frame_rate) // self.frame_rate, self.frame_rate)
            vutil.writetxt(output_shot_html, output)

    def vastProofreadSeg(self, frame_index = 0, shot_js = None, output_folder = None):
        # Output im.vsvi and seg.vsvi for VAST-lite proofreading
        frame_suf = ''
        if isinstance(frame_index, int):
            frame_index, frame_suf = self.getFrameIndex(frame_index, shot_js)
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
                output = vsvi_proofread_seg % (meta, image_template, 0, \
                                                   image_template, frame_size[1], frame_size[0], \
                                                   frame_index_str, frame_size[1], frame_size[0], \
                                                   len(frame_index), meta)
                vutil.writetxt(output_vsvi, output)
