import os
import glob
import json
from .videoProcessor import videoProcessor
from .videoProofreader import videoProofreader
from .videoVisualizer import videoVisualizer
from .videoData import videoData
from . import videoUtil as vutil

class videoTool(object):
    def __init__(self, videos_txt='', project_txt=''):
        self.proofreader = videoProofreader()
        self.processor = videoProcessor()
        self.visualizer = videoVisualizer()
        self.data = videoData()

        self.videos_name = None
        if len(videos_txt) > 0:
            self.setVideoList(videos_txt)
        if len(project_txt) > 0:
            self.data.setProjectParam(project_txt)
    
    def setVideoList(self, videos_txt):
        self.videos_txt = videos_txt
        self.videos_name = [x[:-1].strip() for x in vutil.readtxt(videos_txt)]

    def setProjectParam(self, project_txt):
        self.data.setProjectParam(project_txt)

    def extractVideoInfo(self, videos_json=''):
        if self.videos_name is not None:
            if len(videos_json) == 0:
                videos_json = self.videos_txt.replace('.txt', '.json')
            output = {}
            for video_name in self.videos_name:
                self.data.setVideo(video_name)
                num_frame = len(glob.glob(os.path.join(self.data.frame_folder, '*.' + self.data.frame_suffix)))
                video_size, video_fps, video_duration = vutil.getVideoInfo(self.data.video_file)
                output[video_name] = {'url': self.data.video_url,
                                     'num_frame': num_frame,
                                     'fps': float(video_fps),
                                     'duration': video_duration,
                                     'size': [int(x) for x in video_size.split('x')]}
            json.dump(output, open(videos_json, 'w'))

    def process(self, cmd='', job_id = 0, job_num = 1):
        # sequential jobs
        if cmd == 'extract-info':
            self.extractVideoInfo()
        else:
            # parallized jobs
            for video_name in self.videos_name[job_id::job_num]:
                self.data.setVideo(video_name)

                if cmd == 'download':
                    self.processor.downloadVideo(self.data.video_url, self.data.video_folder)
                elif cmd == 'extract-frame':
                    self.processor.extractFrames(self.data.video_file, self.data.frame_folder)
                elif cmd == 'shot-detection':
                    self.processor.shotDetection(self.data.frame_template, self.data.stats_folder)
                elif cmd == 'web-setup':
                    self.processor.frameCopy(self.data.frame_template, frame_downsample = self.data.frame_size[1]//320, frame_rate=vtool.data.video_frame_step)
                    self.processor.shotDetection(frame_template, result_folder)
                else:
                    raise Exception('command %s not found.'%cmd)
