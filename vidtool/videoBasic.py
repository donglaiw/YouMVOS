import os
import shutil
import json
import imageio
import numpy as np
from . import videoUtil as vutil

class videoBasic(object):
    def __init__(self, job_id = 0, job_num = 1, redo = False):
        self.job_id = job_id
        self.job_num = job_num
        self.redo = redo

        self.video_all_info = None
        self.video_all_name = None
    
    def setSingleProcess(self):
        self.job_id = 0
        self.job_num = 1

    def setRedo(self, redo):
        self.redo = redo

    def setFolders(self, data_folder, web_folder = '', share_folder = ''):
        # data_folder: original mp4/frames
        # web_folder: web-based proofreading
        # share_folder: desktop-based proofreading
        self.data_folder = data_folder
        self.web_folder = web_folder
        self.share_folder = share_folder
    
    # all videos
    def setInputVideoTxt(self, input_file):
        vutil.checkVideoTxt(input_file)
        video_all_info = vutil.readtxt(input_file)
        self.video_all_name = [line.split(',')[0] for line in video_all_info]

    def setInputVideoJson(self, input_file):
        self.video_all_info = json.load(open(input_file))
        self.video_all_name = self.video_all_info.keys()

    # one video
    def setVideoInfo(self, video_name, frame_num = -1, frame_rate = -1):
        self.video_name = video_name
        self.video_url = video_name[max(0, video_name.rfind('/')):]
        self.video_frame_num = frame_num
        self.video_frame_rate = frame_rate
        if frame_num < 0:
            self.video_frame_num = self.video_all_info[video_name]['num_frame']
        if frame_rate < 0:
            self.video_frame_rate = self.video_all_info[video_name]['fps']
        self.video_frame_rate = int(np.round(self.video_frame_rate))

        self.video_data_folder = self.data_folder + '/' + self.video_name + '/'
        self.video_web_folder = self.web_folder + '/' + self.video_name + '/'
        self.video_share_folder = self.share_folder + '/' + self.video_name + '/'

    def getFrameName(self, frame_id):
        frame_name = self.video_data_folder+'frame/image_%05d.png'
        if frame_id >= 0:
            frame_name = frame_name % (frame_id+1)
        return frame_name 

    def getFrame(self, frame_id):
        return imageio.imread(self.getFrameName(frame_id))

    def copyFrames(self, output_folder, frame_rate = -1, frame_downsample = 1):
        vutil.mkdir(output_folder)
        if frame_rate < 0:
            frame_rate = self.video_frame_rate

        frame_ids = np.arange(0, self.video_frame_num, self.video_frame_rate)
        for frame_id in frame_ids[self.job_id :: self.job_num]:
            frame_name_in = self.getFrameName(frame_id)
            frame_name_out = output_folder + frame_name_in[frame_name_in.rfind('/'):]
            if not os.path.exists(frame_name_out):
                if frame_downsample != 1:
                    output = imageio.imread(frame_name_in)[::frame_downsample, ::frame_downsample]
                    imageio.imwrite(frame_name_out, output)
                else:
                    shutil.copy(frame_name_in, frame_name_out)

    # Different sets of keyframes.
    def getKeyframeSuf(self, frame_index = 0):
        frame_suf = ''
        if isinstance(frame_index, int):
            frame_suf = ['_all', '_shot_bd', '_shot'][frame_index]
        return frame_suf

    def getKeyframeSegmentFolder(self, output_folder = None, frame_index = 0):
        frame_suf = self.getKeyframeSuf(frame_index)
        if output_folder is None:
            output_folder = self.video_share_folder
        output_folder += 'seg%s/' % frame_suf
        return output_folder

    def getKeyframeIndex(self, frame_index = 0, shot_folder = None):
        # returninput can either be the input frame index
        # or the frame_index for the pre-defined frame index
        if not isinstance(frame_index, int):
            return frame_index
        else:
            frames = np.arange(0, self.video_frame_num, self.video_frame_rate)
            if frame_index == 0:
                # All frames
                return frames
            else:
                shot_js = self.getShotJs(shot_folder)
                shot_info = vutil.readtxt(shot_js)[0]
                shot_start = [int(x) for x in shot_info[shot_info.find('=')+2:shot_info.find(';')-1].split(',')] 
                shot_start += [len(frames) - 1]
                shot_selection = np.array([int(x) for x in shot_info[shot_info.rfind('=')+2:-2].split(',')]) 
                if frame_index == 1: 
                    # Boundary frames in selected shots
                    frame_id = []
                    for shot_id in np.where(shot_selection == 0)[0]:
                        frame_id += [shot_start[shot_id], shot_start[shot_id+1] - 1]
                    # Exist single-frame shots
                    frame_id = np.unique(frame_id)
                elif frame_index == 2: 
                    # All frames in selected shots
                    for shot_id in np.where(shot_selection == 0)[0]:
                        frame_id += range(shot_start[shot_id], shot_start[shot_id+1])
                return frames[frame_id]

    # Shot-related files.
    def getShotTxt(self, shot_file = None):
        if shot_file is None:
            shot_file = self.video_data_folder
        # input folder -> filename 
        if shot_file[-1] == '/':
            shot_file += 'shot.txt'
        return shot_file

    def getShotJs(self, shot_file = None):
        if shot_file is None:
            shot_file = self.video_web_folder + '../saved/'
        # input folder -> filename 
        if shot_file[-1] == '/':
            shot_file += '%s_shot.js' % (self.video_url)
        return shot_file

    def getShotHtml(self, shot_file = None):
        if shot_file is None:
            shot_file = self.video_web_folder + '../test/'
        # input folder -> filename 
        if shot_file[-1] == '/':
            shot_file += '%s_shot.html' % (self.video_url)
        return shot_file
