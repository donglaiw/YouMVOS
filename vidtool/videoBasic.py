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
        self.data_folder = data_folder + '/'
        self.web_folder = web_folder + '/'
        self.share_folder = share_folder + '/'
    
    # all videos
    def setInputVideoTxt(self, input_file):
        vutil.checkVideoTxt(input_file)
        video_all_info = vutil.readtxt(input_file)
        self.video_all_name = [line.split(',')[0] for line in video_all_info]

    def setInputVideoJson(self, input_file):
        self.video_all_info = json.load(open(input_file))
        self.video_all_name = list(self.video_all_info.keys())

    # one video
    def setVideoInfo(self, video_name, frame_num = -1, frame_rate = -1):
        self.video_name = video_name
        self.video_url = video_name[video_name.rfind('/')+1:]
        self.video_frame_num = frame_num
        self.video_frame_rate = frame_rate
        if self.video_all_info is not None:
            if frame_num < 0:
                self.video_frame_num = self.video_all_info[video_name]['num_frame']
            if frame_rate < 0:
                self.video_frame_rate = self.video_all_info[video_name]['fps']
        self.video_frame_rate = int(np.round(self.video_frame_rate))

        self.video_data_folder = self.data_folder + '/' + self.video_name + '/'
        self.video_web_folder = self.web_folder + '/%s/' + self.video_name + '/'
        self.video_share_folder = self.share_folder + '/' + self.video_name + '/'

    def getFrameName(self, frame_id = 0, output_folder = None, suffix = ''):
        if output_folder is None:
            output_folder = self.video_data_folder + 'frame%s/' % suffix
        if frame_id == -2:
            return output_folder
        frame_name = output_folder + 'image_%05d.png'
        if frame_id >= 0:
            frame_name = frame_name % (frame_id+1)
        return frame_name 

    def getFrame(self, frame_id = 0, output_folder = None):
        return imageio.imread(self.getFrameName(frame_id, output_folder))

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
    def getKeyframeSuf(self, option = 0):
        frame_suf = ''
        if isinstance(option, int):
            frame_suf = ['_all', '_shot_bd', '_shot'][option]
        return frame_suf

    def getKeyframeSegmentFolder(self, output_folder = None, option = 0):
        frame_suf = self.getKeyframeSuf(option)
        if output_folder is None:
            output_folder = self.video_share_folder
        output_folder += 'seg%s/' % frame_suf
        return output_folder

    def getKeyframeIndex(self, option = 0, shot_folder = None, frame_rate = -1):
        # returninput can either be the input frame index
        # or the frame_index for the pre-defined frame index
        if frame_rate < 0:
            frame_rate = self.video_frame_rate
        keyframes = np.arange(0, self.video_frame_num, frame_rate)
        if option == 0:
            # All frames
            return keyframes
        else:
            # Js: natural index without the framerate info
            shot_js = self.getShotJs(shot_folder)
            shots, shot_selection = self.convertShotJsToArr(shot_js, option=1)
            if option == 1: 
                # Boundary frames in selected shots
                # Exist single-frame shots
                frame_id = np.unique(shots[shot_selection == 0])
            elif option == 2: 
                # All frames in selected shots
                frame_id = []
                for shot_id in np.where(shot_selection == 0)[0]:
                    frame_id += range(shots[shot_id, 0], shots[shot_id, 1]+1)
            return keyframes[frame_id]

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
    
    def convertShotJsToArr(self, shot_js, option = 0, frame_rate = -1):
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
                
        shot_selection = np.array([int(x) for x in shot_info[shot_info.rfind('=')+2:-1].split(',')]) 
        return shots, shot_selection

    def convertShotArrToJs(self, shots, frame_rate = -1):
        if frame_rate < 0 :
            frame_rate = self.video_frame_rate

        # Take the ceil for the start frame.
        # Can be repeated due to frame_rate downsample
        shots = np.unique((shots[:, 0] + frame_rate - 1) // frame_rate)
        output_js = 'var shot_start_str="'+','.join([str(x) for x in shots])+'";'
        output_js += 'var shot_selection_str="'+','.join([str(0) for x in shots])+'";'
        return output_js
