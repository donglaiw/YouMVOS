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

    def webProofreadShot(self, input_txt = None, suf='shot', frame_rate = -1):
        # Convert shot_txt into js and html
        if frame_rate < 0 :
            frame_rate = self.video_frame_rate

        output_js = self.data.getJs('_' + suf)
        if self.data.redo or not os.path.exists(output_js):
            print('do js')
            input_file = self.getTxt(input_txt, suf)
            shots = np.loadtxt(input_file).astype(int)
            output_var = self.convertShotArrToJs(shots, frame_rate)
            vutil.writetxt(output_js, output_var)

        output_html = self.data.getHtml('_shot')
        if self.data.redo or not os.path.exists(output_html):
            print('do shot')
            output = html_shot % ('../../../frame_ds/', self.data.video_name, (self.data.video_frame_num + self.data.video_frame_rate - 1) // self.data.video_frame_rate, self.data.video_frame_rate)
            vutil.writetxt(output_html, output)

    def webProofreadShotSR(self, suf_in = '_shot', suf_out = '_shot_out', frame_rate_in = -1, frame_step = -1):
        if frame_rate_in < 0:
            frame_rate_in = self.data.video_frame_rate
        if frame_step < 0:
            frame_step = self.data.video_frame_step
        # Convert shot.js into js and html
        output_js = self.data.getJs(suf_out)
        if self.data.redo or not os.path.exists(output_js):
            shots, shots_sel = self.data.loadShotJs(shot_js=suf_in)

            shots_v2 = shots * frame_step 
            # use frame_diff to refine shot
            frame_diff = np.loadtxt(self.data.getTxt(suf = 'rgb_diff')).astype(int)
            # first element: f1-f0
            rest = (-len(frame_diff)) % frame_step
            frame_diff = np.hstack([frame_diff, np.zeros(rest,int)]).reshape(-1,frame_step).max(axis=1)
            # match to shots_id, no need for last chunk
            for i in range(len(shots)):
                fid = shots_v2[i]
                if fid == 0:
                    continue
                bid = np.argmax(frame_diff[fid-frame_step:fid])
                shots_v2[i] = fid - frame_step + 1 + bid
                
            output_var = vutil.convertShotToJs(shots_v2, shots_sel)
            vutil.writetxt(output_js, output_var)
        output_html = self.data.getHtml(suf_out)
        if self.data.redo or not os.path.exists(output_html):
            print('do shot')
            output = html_shot % ('../../../frame_ds/', self.data.video_name, (self.data.video_frame_num + frame_step - 1) // frame_step, frame_step, suf_out)
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

    def webProofreadSeg(self, seg_prefix='refine_', seg_suffix='_cluster', input_txt = None, frame_rate = -1):
        # Convert shot_txt into js and html
        if frame_rate < 0 :
            frame_rate = self.data.video_frame_rate

        output_html = self.data.getHtml('_seg')
        vutil.mkdir(output_html, 'dir')
        if self.data.redo or not os.path.exists(output_html):
            print('do seg')
            if input_txt is None: # load what is available
                overlay_files = sorted(glob(output_html[:output_html.rfind('/')] + '/../../../seg_ds/'+self.video_name+'/' + seg_prefix + '*.png'))
                overlay_id = ','.join([str(int(x[x.rfind('_')+1:-4])) for x in overlay_files]) 
            elif '.txt' not in input_txt:
                # load shot result
                overlay_id = ','.join([str(x) for x in self.data.getFrameIndex(input_txt)])
            else:
                overlay_id = vutil.readtxt(input_txt)[:-1]
            output = html_seg % ('../../../frame_ds/', '../../../seg_ds/', self.data.video_name, overlay_id, self.data.video_frame_num, seg_prefix, seg_suffix, self.data.video_frame_rate)
            vutil.writetxt(output_html, output)

    def webProofreadCharacter(self, video_names, seg_folder='seg_out', seg_pref='manual_'):
        # one page for many videos
        output_html = self.data.PROOFREADER_HTML_TEST % (self.data.video_genre, 'dsp_character', '')
        vutil.mkdir(output_html, 'dir')
        if self.data.redo or not os.path.exists(output_html):
            output = html_character_header % '../../../seg_ds/'
            for video_name in video_names:
                self.data.setVideoInfo(video_name)
                info_txt = self.data.FRAME_ROOT.format(self.data.video_name) + '/%s.txt' % (seg_folder)
                if os.path.exists(info_txt):
                    info = vutil.readtxt(info_txt)
                    info_str = vutil.converListToJsArr(info)
                    output += html_character_body % (self.data.video_name, info_str, self.data.video_frame_rate, seg_pref)
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
        vutil.mkdir(output_folder)
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

    def vastProofreadSegStat(self, seg_folder = 'seg_out', seg_root = None):
        max_obj = 20
        output_txt = self.data.FRAME_ROOT.format(self.data.video_name) + '/%s.txt' %(seg_folder)

        if self.data.redo or not os.path.exists(output_txt):
            if seg_root is None:
                seg_root = self.data.FOLDER_DOWNLOAD
            mask_template =  seg_root + self.data.video_name + '/%s/'%seg_folder
            mask_names = sorted(glob(mask_template + '*.png'))
            k_ind = [None] * max_obj
            k_id = np.zeros(max_obj, int)
            for mask_name in mask_names:
                mid = mask_name[mask_name.rfind('/')+1:]
                if '_s' in mid:
                    mid = int(mid[mid.rfind('_s')+2:-4])
                else:
                    mid = int(mid[mid.rfind('_')+1:-4])
                seg = vutil.vast2Seg(imageio.imread(mask_name))
                uid = np.unique(seg)
                #print(uid)
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
