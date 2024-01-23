import os,sys
import math
import numpy as np
from glob import glob
import imageio

from .htmlGenerator import *
from . import videoUtil as vutil

class videoProofreader(object):
    def __init__(self):
        self.redo = False
        # default values
        self.folder_proofread = ''
        self.frame_offset = 1
        self.frame_fmt = 'image_%05d.png'
        self.seg_fmt = 'seg_%05d.png'
    
    def setRedo(self, redo):
        self.redo = redo

    def setFolderInfo(self, folder_proofread, frame_offset):
        # for all videos
        self.folder_proofread = folder_proofread
        self.frame_offset = frame_offset

    def webProofreadScene(self, input_txt, video_path, frame_step, frame_template):
        # Convert cluster.txt into js and html
        scenes = np.loadtxt(input_txt).astype(int)
        filename = os.path.basename(input_txt)
        filename_nosuf = filename[:filename.rfind('.')]
        web_frame_template = frame_template
        video_url = video_path[video_path.rfind('/')+1:] if '/' in video_path else video_path
        web_file = os.path.join(self.folder_proofread, video_path)
        web_folder = os.path.dirname(web_file)
        if self.redo or not os.path.exists(web_folder):
            vutil.mkdir(web_folder)
            os.chmod(web_folder, 0o777)

        output_html = web_file + '_' + filename_nosuf + '.html'
        output_js = web_file + '_' + filename_nosuf + '.js'
        output_js_local = video_url + '_' + filename_nosuf + '.js'

        if self.redo or not os.path.exists(output_js):
            if 'shot' in filename: # shot detection
                output_var = vutil.convertShotToJs(scenes, frame_rate = frame_step)
            elif 'cluster' in filename: # frame cluster
                output_var = vutil.convertClusterToJs(scenes)
            vutil.writetxt(output_js, output_var)

        if self.redo or not os.path.exists(output_html):
            if 'shot' in filename: # shot detection
                frame_num = scenes[-1,-1] + 1
            elif 'cluster' in filename: # frame cluster
                frame_num = len(scenes)
            frame_num_web = (frame_num + frame_step - 1) // frame_step

            if 'shot' in filename: # shot detection
                output = getHtmlShot(web_frame_template, frame_num_web, frame_step, self.frame_offset, output_js_local)
            elif 'cluster' in filename: # frame cluster
                output = getHtmlCluster(web_frame_template, frame_num_web, frame_step, self.frame_offset, output_js_local)
            vutil.writetxt(output_html, output)

    def webProofreadShotSR(self, suf_in = '_shot', suf_out = '_shot_out', frame_rate_in = -1, frame_step = -1):
        if frame_rate_in < 0:
            frame_rate_in = self.data.video_frame_rate
        if frame_step < 0:
            frame_step = self.data.video_frame_step
        sr_ratio = frame_rate_in // frame_step
        # Convert shot.js into js and html
        output_js = self.data.getJs(suf_out)
        if self.data.redo or not os.path.exists(output_js):
            if '_shot' in suf_in:
                shots, shots_sel = self.data.loadShotJs(shot_js=suf_in)
            else:
                clusters, clusters_sel = self.data.loadClusterJs(cluster_js=suf_in)
                shots, shots_sel = vutil.convertClusterListToShot(clusters, clusters_sel)
                if (shots[1:, 0] - shots[:-1, 1] != 1).sum()>0:
                    # exist missing frames
                    import pdb; pdb.set_trace()
                shots = shots[:,0]

            shots_v2 = shots * sr_ratio 
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
                bid = np.argmax(frame_diff[fid-sr_ratio:fid])
                shots_v2[i] = fid - sr_ratio + 1 + bid
                
            output_var = vutil.convertShotToJs(shots_v2, shots_sel)
            vutil.writetxt(output_js, output_var)
        output_html = self.data.getHtml(suf_out)
        if self.data.redo or not os.path.exists(output_html):
            print('do shot')
            output = html_shot % ('../../../frame_ds/', self.data.video_name, (self.data.video_frame_num + frame_step - 1) // frame_step, frame_step, suf_out)
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
                overlay_id = self.data.getFrameIndex(input_txt)
                if overlay_id is None:
                    # can be missing files
                    return 0
                overlay_id = ','.join([str(x) for x in overlay_id])
            else:
                overlay_id = vutil.readtxt(input_txt)[:-1]
            output = html_seg % ('../../../frame_ds/', '../../../seg_ds/', self.data.video_name, overlay_id, self.data.video_frame_num, seg_prefix, seg_suffix, self.data.video_frame_rate)
            vutil.writetxt(output_html, output)

    def webProofreadCharacter(self, video_names, seg_folder='seg_out', seg_pref='manual_', output_html = None):
        # one page for many videos
        if output_html is None:
            output_html = self.data.PROOFREADER_HTML_TEST % (self.data.video_genre, 'dsp_character', '')
        vutil.mkdir(output_html, 'dir')
        num=5
        if self.data.redo or not os.path.exists(output_html):
            output = html_character_header % '../../../seg_ds/'
            for video_name in video_names:
                self.data.setVideoInfo(video_name)
                info_txt = self.data.FOLDER_DOWNLOAD.format(self.data.video_name) + '/%s.txt' % (seg_folder)
                if os.path.exists(info_txt):
                    info = vutil.readtxt(info_txt)
                    # skip empty ones
                    if len(info)>0:
                        for j in range(len(info)):
                            tmp = info[j][:-1].split(',')
                            if (len(tmp)//num) > 0:
                                tmp = tmp[::(len(tmp)//num)]
                            info[j] = ','.join([str(x) for x in tmp]) + '\n'
                        info_str = vutil.converListToJsArr(info)[:-1]
                        output += html_character_body % (self.data.video_name, info_str, self.data.video_frame_step, seg_pref)
                    else:
                        print('empty:', info_txt)
                else:
                    print('no:', info_txt)
            output += html_character_footer
            vutil.writetxt(output_html, output)

    def vastProofreadSeg(self, frame_ids, frame_size, output_folder, vsvis=[], vsvis_source=[], mask_id_func=None, frame_ids_after=-1):
        # Output im.vsvi and/or seg.vsvi for VAST-lite proofreading
        frame_ids = frame_ids[frame_ids > frame_ids_after]
        vutil.mkdir(output_folder)
        for vsvi, vsvi_source in zip(vsvis, vsvis_source):
            output_vsvi =  os.path.join(output_folder, vsvi + '.vsvi')
            if self.redo or not os.path.exists(output_vsvi):
                # has to be on windows
                print(output_vsvi)
                if 'im' in vsvi:
                    fmt = self.frame_fmt
                else:
                    fmt = self.seg_fmt
                    if mask_id_func is not None:
                        frame_ids = mask_id_func(frame_ids)
                frame_ids_str = vutil.converArrToStr(frame_ids)
                image_template = r'.\%s\%s' % (vsvi_source, fmt)
                output = getVsvi(vsvi, image_template, frame_ids_str, frame_size)
                vutil.writetxt(output_vsvi, output)

        # in case of index conversion
        if mask_id_func is None:
            seg_ids = frame_ids
        else:
            seg_ids = mask_id_func(frame_ids)

        frame_ids_str = [vutil.converArrToStr(frame_ids), vutil.converArrToStr(seg_ids)]


    def vastProofreadSegStat(self, seg_folder = 'seg_out', seg_root = None):
        max_obj = 20
        output_txt = self.data.FOLDER_DOWNLOAD.format(self.data.video_name) + '/%s.txt' %(seg_folder)

        if self.data.redo or not os.path.exists(output_txt):
            if seg_root is None:
                seg_root = self.data.FOLDER_DOWNLOAD
            mask_template =  seg_root.format(self.data.video_name) + '/%s/'%seg_folder
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
