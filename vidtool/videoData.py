import os
import shutil
import json
import imageio
import numpy as np

from . import videoUtil as vutil
from .videoParam import videoParam 

class videoData(object):
    def __init__(self, redo = False):
        self.setParams()

        self.redo = redo
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
            self.video_duration = self.video_all_info[video_name]['duration']
        self.video_frame_rate = int(np.round(self.video_frame_rate))
        
        # output 6fps
        if self.video_frame_rate in [25,30]:
            self.video_frame_step = 5
        elif self.video_frame_rate in [24]:
            self.video_frame_step = 4
        elif self.video_frame_rate in [27]:
            self.video_frame_step = 3
        else:
            raise ValueError('unknown frame rate %d' % self.video_frame_rate)


    ####
    # I/O for frames
    def getFrameName(self, frame_id = 0, frame_name = None, suffix = ''):
        if frame_name is None:
            frame_name = self.FRAME_NAME.format(self.video_name, suffix)
        if frame_id == -2: # return directory
            return os.path.dirname(frame_name) + '/'
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
                if '_out' in option:
                    frame_rate = self.video_frame_step
            frame_ids = np.arange(0, self.video_frame_num, frame_rate) + self.FRAME_OFFSET

            if 'shot' in option:
                if '_out' in option and input_file is None:
                    input_file = '_shot_out'
                # Js: natural index without the framerate info
                shots, shot_selection = self.loadShotJs(input_file, option='2d', frame_rate=frame_rate)
                if 'shot_selected_min' in option: 
                    # first frames in selected shots
                    # Exist single-frame shots
                    frame_ids = frame_ids[np.unique(shots[shot_selection == 0, 0])]
                elif 'shot_selected_list' in option: 
                    # All frames in selected shots
                    frame_ids_list = [None] * (shot_selection == 0).sum()
                    for i, shot_id in enumerate(np.where(shot_selection == 0)[0]):
                        frame_ids_list[i] = frame_ids[range(shots[shot_id, 0], shots[shot_id, 1]+1)]
                    frame_ids = frame_ids_list

                elif 'shot_selected' in option: 
                    # All frames in selected shots
                    frame_ids_list = []
                    for shot_id in np.where(shot_selection == 0)[0]:
                        frame_ids_list += list(frame_ids[range(shots[shot_id, 0], shots[shot_id, 1]+1)])
                    frame_ids = np.array(frame_ids_list)
            elif 'cluster' in option:
                if '_out' in option and input_file is None:
                    input_file = '_cluster_out'
                cluster_ids = self.loadClusterJs(input_file, option)
                frame_ids = frame_ids[cluster_ids]
        return frame_ids

    ####
    # I/O for proofreading files
    def getTxt(self, txt_file = None, suf = ''):
        if txt_file is None:
            txt_file = self.FOLDER_DOWNLOAD + self.video_name + '/'
        # input folder -> filename 
        if txt_file[-1] == '/':
            txt_file += suf + '.txt'
        return txt_file

    def getJs(self, suf = ''):
        if suf is None:
            suf = '_shot'
        return self.PROOFREADER_JS_SAVE % (self.video_genre, self.video_url, suf)

    def getHtml(self, suf = ''):
        return self.PROOFREADER_HTML_TEST % (self.video_genre, self.video_url, suf)

    def loadClusterJs(self, cluster_js = None, option = 'cluster'):
        if cluster_js is None:
            cluster_js = self.getJs('_cluster')
        cluster_info = vutil.readtxt(cluster_js)[0].strip()
        shot_ids = vutil.convertClusterStrToClusterList(cluster_info[cluster_info.find('=')+2:cluster_info.rfind('var')-2]) 
        if '_factor' in option:
            shot_ids = [list(np.array(x)*self.video_frame_rate+self.FRAME_OFFSET) for x in shot_ids]
        shot_selection = np.array([int(x) for x in cluster_info[cluster_info.rfind('=')+2:cluster_info.rfind('"')].split(',')]) 
        if option == 'cluster':
            return shot_ids, shot_selection
        if 'selected_' in option:
            shot_ids = [shot_ids[x] for x in np.where(shot_selection == 0)[0]]
            if 'minA' in option:
                shot_ids = [sorted(x) for x in shot_ids]
            elif 'min' in option:
                shot_ids = [min(x) for x in shot_ids]
            if 'midA' in option:
                shot_ids = [list(np.array(x)[np.argsort(x)[len(x)//2:]]) +\
                            list(np.array(x)[np.argsort(x)[len(x)//2-1::-1]]) for x in shot_ids]
            elif 'mid' in option:
                shot_ids = [x[np.argsort(x)[len(x)//2]] for x in shot_ids]
            if 'maxA' in option:
                shot_ids = [sorted(x, reverse=True) for x in shot_ids]
            elif 'max' in option:
                shot_ids = [max(x) for x in shot_ids]

        if 'cluster_selected_str' in option:
            return vutil.convertClusterListToStr(shot_ids)
        elif 'cluster_selected_arr' in option:
            return [j for i in shot_ids for j in i]
        elif 'cluster_selected' in option:
            return shot_ids

    def loadShotJs(self, shot_js='_shot', option = 0, frame_rate = -1):
        shot_js = self.getJs(shot_js)
        shot_info = vutil.readtxt(shot_js)[0].strip()
        # start frame (N)
        shots = np.array([int(x) for x in shot_info[shot_info.find('=')+2:shot_info.find(';')-1].split(',')])
        if option in ['2d', 2]:
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
