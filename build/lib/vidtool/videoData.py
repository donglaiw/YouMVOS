import os
import shutil
import json
import imageio
import numpy as np

from . import videoUtil as vutil
from .videoParam import videoParam 

class videoData(object):
    def __init__(self):
        self.setParams()
        self.video_all_info = None
        self.video_all_name = None
   
    ####
    # path and filename param
    # data/param.json
    def setParams(self):
        param = videoParam()
        self.__dict__ = param.__dict__.copy() 

    ####
    # I/O for video info
    # data/video_v0.txt
    def setInputVideoTxt(self, input_file):
        vutil.checkVideoTxt(input_file)
        video_all_info = vutil.readtxt(input_file)
        self.video_all_name = [line.split(',')[0] for line in video_all_info]

    # after download videos and extract frames
    # vutil.VideoTxtToJson: generate data/video_v0.json
    def setInputVideoJson(self, input_file):
        self.video_all_info = json.load(open(input_file))
        self.video_all_name = list(self.video_all_info.keys())

    # current video
    def setVideoInfo(self, video_name, frame_num = -1, frame_rate = -1):
        self.video_name = video_name
        self.video_genre = video_name[:video_name.rfind('/')]
        self.video_url = video_name[video_name.rfind('/')+1:]
        self.video_frame_num = frame_num
        self.video_frame_rate = frame_rate
        if self.video_all_info is not None:
            if frame_num < 0:
                self.video_frame_num = self.video_all_info[video_name]['num_frame']
            if frame_rate < 0:
                self.video_frame_rate = self.video_all_info[video_name]['fps']
            self.video_frame_size = self.video_all_info[video_name]['size']
        self.video_frame_rate = int(np.round(self.video_frame_rate))

    ####
    # I/O for frames
    def getFrameName(self, frame_id = 0, frame_name = None, suffix = ''):
        if frame_name is None:
            frame_name = self.FRAME_NAME.format(self.video_name, suffix)
        if frame_id == -2: # return directory
            return os.path.dirname(frame_name)
        if frame_id >= 0:
            frame_name = frame_name % frame_id
        return frame_name 

    def getFrameImage(self, frame_id = 0, output_folder = None):
        return imageio.imread(self.getFrameName(frame_id, output_folder))

    def getFrameIndex(self, option = 'all', frame_rate = -1, frame_num = -1, input_file = None):
        # returninput can either be the input frame index
        # or the frame_index for the pre-defined frame index
        if option == 'uniform':
            # uniform N-frame
            frame_ids = np.linspace(0, self.video_frame_num - 1, frame_num).astype(int)
        else:
            if frame_rate < 0:
                frame_rate = self.video_frame_rate
            frame_ids = np.arange(0, self.video_frame_num, frame_rate) + self.FRAME_OFFSET

            if option == 'para':
                # divided by job
                num_per_job = (len(frame_ids) + self.job_num - 1) // self.job_num
                frame_range = range(self.job_id * num_per_job, min((self.job_id + 1) * num_per_job, len(frame_ids)))
                frame_ids = frame_ids[frame_range]
            elif 'shot' in option:
                # Js: natural index without the framerate info
                shots, shot_selection = self.convertShotJsToArr(input_file, option=1)
                if option == 'shot': 
                    # first frames in selected shots
                    # Exist single-frame shots
                    frame_ids = frame_ids[np.unique(shots[shot_selection == 0, 0])]
                elif option == 'shot_all': 
                    # All frames in selected shots
                    frame_ids_list = []
                    for shot_id in np.where(shot_selection == 0)[0]:
                        frame_ids_list += list(frame_ids[range(shots[shot_id, 0], shots[shot_id, 1]+1)])
                    frame_ids = np.array(frame_ids_list)
                elif option == 'shot_all_list': 
                    # All frames in selected shots
                    frame_ids_list = [None] * (shot_selection == 0).sum()
                    for i, shot_id in enumerate(np.where(shot_selection == 0)[0]):
                        frame_ids_list[i] = frame_ids[range(shots[shot_id, 0], shots[shot_id, 1]+1)]
                    frame_ids = frame_ids_list
        return frame_ids

    ####
    # I/O for proofreading files
    def getTxt(self, txt_file = None, suf = ''):
        if txt_file is None:
            txt_file = self.video_folder_download
        # input folder -> filename 
        if txt_file[-1] == '/':
            txt_file += suf + '.txt'
        return txt_file

    def getJs(self, js_file = None, suf = ''):
        if js_file is None:
            js_file = self.PROOFREADER_JS_SAVE % (self.video_genre, self.video_url, suf)
        else: # input folder -> filename 
            if js_file[-1] == '/':
                js_file += '%s%s.js' % (self.video_url, suf)
        return js_file

    def getHtml(self, html_file = None, suf = ''):
        if html_file is None:
            html_file = (self.video_folder_web % 'proofread/')[:-1]
            html_file = html_file[:html_file.rfind('/')] + '/test/'
        # input folder -> filename 
        if html_file[-1] == '/':
            html_file += '%s%s.html' % (self.video_url, suf)
        return html_file

    def loadClusterJs(self, cluster_js, option = ''):
        cluster_js = self.getJs(cluster_js, '_cluster')
        cluster_info = vutil.readtxt(cluster_js)[0].strip()
        shot_index = vutil.convertClusterStrToClusterList(cluster_info[cluster_info.find('=')+2:cluster_info.rfind('var')-2]) 
        shot_selection = np.array([int(x) for x in cluster_info[cluster_info.rfind('=')+2:cluster_info.rfind('"')].split(',')]) 
        if option == '':
            return shot_index, shot_selection
        if 'selected_' in option:
            shot_index = [shot_index[x] for x in np.where(shot_selection == 0)[0]]
            if option == 'selected_list':
                return shot_index
            elif option == 'selected_str':
                return vutil.convertClusterListToStr(shot_index)


    def convertShotJsToArr(self, shot_js, option = 0, frame_rate = -1):
        shot_js = self.getJs(shot_js, '_shot')
        shot_info = vutil.readtxt(shot_js)[0].strip()
        # start frame (N)
        shots = np.array([int(x) for x in shot_info[shot_info.find('=')+2:shot_info.find(';')-1].split(',')]) 
        if option in [1, 2]:
            # start-end frame (N x 2)
            if frame_rate < 0:
                frame_rate = self.video_frame_rate
            frame_num = (self.video_frame_num + frame_rate - 1) // frame_rate 
            shots = np.vstack([shots, \
                               list(shots[1:] - 1) + [frame_num - 1]]).T
            if option == 2:
                # back to original index
                frame_ids = np.arange(0, self.video_frame_num, frame_rate)
                shots = frame_ids[shots]
                
        shot_selection = np.array([int(x) for x in shot_info[shot_info.rfind('=')+2:shot_info.rfind('"')].split(',')]) 

        return shots, shot_selection

    def convertShotArrToJs(self, shots, frame_rate = -1):
        # need consecutive numbers for easy editing
        if frame_rate < 0 :
            frame_rate = self.video_frame_rate

        # Take the ceil for the start frame.
        # Can be repeated due to frame_rate downsample
        if shots.ndim == 1:
            shots = [(shots[0] + frame_rate - 1) // frame_rate]
        else:
            shots = np.unique((shots[:, 0] + frame_rate - 1) // frame_rate)
        output_js = 'var shot_start_str="'+','.join([str(x) for x in shots])+'";'
        output_js += 'var shot_selection_str="'+','.join([str(0) for x in shots])+'";'
        return output_js
