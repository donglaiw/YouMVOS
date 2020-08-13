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
        self.setGetFrameName()
    
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

        vutil.mkdir(self.video_data_folder)
        vutil.mkdir(self.video_web_folder)
        vutil.mkdir(self.video_share_folder)

    def setGetFrameName(self, getFrameName = None):
        if getFrameName is None:
            def getFrameName(frame_id):
                return self.video_data_folder+'frame/image_%05d.png' % (frame_id+1)
        self.getFrameName = getFrameName

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

    def getFrameIndex(self, option = 0, shot_js = None):
        frames = np.arange(0, self.video_frame_num, self.video_frame_rate)
        if option == 0:
            # All frames
            frame_suf = '_all'
            return frames
        else:
            if shot_js is None:
                # default in the www/ folder
                shot_js = self.video_web_folder + '../saved/%s_shot.js' % (self.video_url)
            elif shot_js[-1] == '/':
                # only provide the folder
                shot_js = shot_js + '%s_shot.js' % (self.video_url)
            shot_info = vutil.readtxt(shot_js)[0]
            shot_start = [int(x) for x in shot_info[shot_info.find('=')+2:shot_info.find(';')-1].split(',')] 
            shot_start += [len(frames) - 1]
            shot_selection = np.array([int(x) for x in shot_info[shot_info.rfind('=')+2:-2].split(',')]) 
            if option == -1: 
                # Boundary frames in selected shots
                frame_suf = '_shot_bd'
                frame_id = []
                for shot_id in np.where(shot_selection == 0)[0]:
                    frame_id += [shot_start[shot_id], shot_start[shot_id+1] - 1]
            elif option == -2: 
                # All frames in selected shots
                frame_suf = '_shot'
                for shot_id in np.where(shot_selection == 0)[0]:
                    frame_id += range(shot_start[shot_id], shot_start[shot_id+1])
            return frames[frame_id], frame_suf

    # shot-level filenames
    def getShotTxt(self, shot_folder = None):
        if shot_folder is None:
            shot_folder = self.video_data_folder
        return shot_folder + 'shot.txt'
    def getShotJs(self, shot_folder = None):
        if shot_folder is None:
            shot_folder = self.video_web_folder + '../saved/'
        return shot_folder + '%s_shot.js' % (self.video_url)
    def getShotHtml(self, shot_folder = None):
        if shot_folder is None:
            shot_folder = self.video_web_folder + '../test/'
        return shot_folder + '%s_shot.html' % (self.video_url)



