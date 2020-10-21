import os,sys
import math
import numpy as np
from glob import glob
import imageio

from ..view import *
from .. import videoUtil as vutil

class videoProofreader(object):
    def __init__(self, data = None):
        self.data= data
    
    def webProofreadFolder(self):
        folder_name = self.data.PROOFREADER_ROOT + self.data.video_genre + '/'
        if not os.path.exists(folder_name + '/saved/'):
            os.mkdir(folder_name + '/saved/')
            os.chmod(folder_name + '/saved/', 0o777)
        vutil.mkdir(folder_name + '/test/')

    def webProofreadShot(self, input_txt = None, frame_rate = -1):
        # Convert shot_txt into js and html
        if frame_rate < 0 :
            frame_rate = self.video_frame_rate

        output_js = self.data.getJs('_shot')
        if self.data.redo or not os.path.exists(output_js):
            print('do js')
            import pdb; pdb.set_trace()
            input_file = self.getTxt(input_txt, 'shot')
            shots = np.loadtxt(input_file).astype(int)
            output_var = self.convertShotArrToJs(shots, frame_rate)
            vutil.writetxt(output_js, output_var)

        output_html = self.data.getHtml('_shot')
        if self.data.redo or not os.path.exists(output_html):
            print('do shot')
            output = html_shot % ('../../../frame_ds/', self.video_name, (self.video_frame_num + self.video_frame_rate - 1) // self.video_frame_rate, self.video_frame_rate)
            vutil.writetxt(output_html, output)

    def webProofreadCluster(self, input_txt = None, frame_rate = -1):
        # Convert shot_txt into js and html
        if frame_rate < 0 :
            frame_rate = self.data.video_frame_rate

        output_js = self.data.getJs('_cluster')
        if False:#self.data.redo or not os.path.exists(output_js):
            print('do js')
            input_file = self.getTxt(input_txt, '_cluster')
            if os.path.exists(input_file):
                shots = np.loadtxt(input_file).astype(int)
            else: # default 1 cluster
                shots = [self.data.getFrameIndex()]
            output_var = vutil.convertClusterListToJs(shots)
            vutil.writetxt(output_js, output_var)

        output_html = self.data.getHtml('_cluster')
        if self.data.redo or not os.path.exists(output_html):
            print('do cluster')
            output = html_cluster % ('../../../frame_ds/', self.data.video_name, (self.data.video_frame_num + self.data.video_frame_rate - 1) // self.data.video_frame_rate, self.data.video_frame_rate, self.data.FRAME_OFFSET)
            vutil.writetxt(output_html, output)

    def webProofreadSeg(self, seg_prefix='refine_', input_txt = None, frame_rate = -1):
        # Convert shot_txt into js and html
        if frame_rate < 0 :
            frame_rate = self.video_frame_rate

        output_html = self.data.getHtml('_seg')
        vutil.mkdir(output_html, 'dir')
        if self.data.redo or not os.path.exists(output_html):
            print('do seg')
            if input_txt is None: # load what is available
                overlay_files = sorted(glob(output_html[:output_html.rfind('/')] + '/../../../seg_ds/'+self.video_name+'/' + seg_prefix + '*.png'))
                overlay_id = ','.join([str(int(x[x.rfind('_')+1:-4])) for x in overlay_files]) 
            elif '.txt' not in input_txt:
                # load shot result
                overlay_id = ','.join([str(x) for x in self.getKeyframeIndex(input_txt, frame_offset = 1)])
            else:
                overlay_id = vutil.readtxt(input_txt)[:-1]
            output = html_seg % ('../../../frame_ds/', '../../../seg_ds/', seg_prefix, self.video_name, overlay_id, (self.video_frame_num + self.video_frame_rate - 1) // self.video_frame_rate, self.video_frame_rate)
            vutil.writetxt(output_html, output)

    def webProofreadCharacter(self, video_names, seg_folder='seg_out'):
        # one page for many videos
        output_html = self.data.PROOFREADER_HTML_TEST % (self.data.video_genre, 'dsp_character', '')
        vutil.mkdir(output_html, 'dir')
        if self.data.redo or not os.path.exists(output_html):
            output = html_character_header % '../../../seg_ds/'
            for video_name in video_names:
                self.data.setVideoInfo(video_name)
                info_txt = self.data.FRAME_ROOT.format(self.data.video_name) + '/%s.txt' % (seg_folder)
                info = vutil.readtxt(info_txt)
                info_str = vutil.converListToJsArr(info)
                output += html_character_body % (self.data.video_name, info_str, self.data.video_frame_rate)
            output += html_character_footer
            vutil.writetxt(output_html, output)

    def vastProofreadSeg(self, frame_ids = 0, frame_suf='', input_js = None):
        # Output im.vsvi and seg.vsvi for VAST-lite proofreading
        if isinstance(frame_ids, str):
            # frame_ids is the option
            frame_ids = self.data.getFrameIndex(frame_ids, input_file = input_js)

        frame_ids_str = vutil.converArrToStr(frame_ids)
        frame_size = np.array(self.data.getFrameImage(frame_ids[0]).shape)

        # output vsvi
        vsvi_type = ['im', 'seg']
        vsvi_filename = ['image_%05d.png','seg_%05d.png']
        output_folder = self.data.PROCESSOR_VAST.format(self.data.video_name)
        for vsvi_id in range(len(vsvi_type)):
            output_vsvi =  output_folder + '%s.vsvi' % (vsvi_type[vsvi_id] + frame_suf)
            if self.data.redo or not os.path.exists(output_vsvi):
                meta = "%s %s" % (self.data.video_name, vsvi_type[vsvi_id])
                image_template = r'.\%s\%s' % (vsvi_type[vsvi_id], vsvi_filename[vsvi_id])
                output = vsvi_seg % (meta, image_template, 0, \
                                                   image_template, frame_size[1], frame_size[0], \
                                                   frame_ids_str, frame_size[1], frame_size[0], \
                                                   len(frame_ids), meta)
                vutil.writetxt(output_vsvi, output)

    def vastProofreadSegStat(self, seg_folder = 'seg_out'):
        max_obj = 20
        output_txt = self.data.FRAME_ROOT.format(self.data.video_name) + '/%s.txt' %(seg_folder)

        if self.data.redo or not os.path.exists(output_txt):
            mask_template = self.data.FOLDER_DOWNLOAD + self.data.video_name + '/%s/'%seg_folder
            mask_names = sorted(glob(mask_template + '*.png'))
            k_ind = [None] * max_obj
            k_id = np.zeros(max_obj, int)
            for mask_name in mask_names:
                mid = int(mask_name[mask_name.rfind('_s')+2:-4])
                seg = vutil.vast2Seg(imageio.imread(mask_name))
                uid = np.unique(seg)
                print(uid)
                uid = uid[uid>0]
                if len(uid) > 0:
                    for ui in uid:
                        if ui not in k_id:
                            new_id = (k_id>0).sum()
                            k_id[new_id] = ui
                            k_ind[new_id] = []
                        k_ind[np.where(k_id==ui)[0][0]] += [mid] 
            # sort by id increasing order
            k_ind = [','.join([str(y) for y in [k_id[x]] + k_ind[x]]) for x in np.argsort(range((k_id>0).sum()))]
            vutil.writetxt(output_txt, k_ind)
