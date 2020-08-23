import os
import json
from . import videoUtil as vutil
from .videoBasic import videoBasic

class videoDownloader(videoBasic):
    def __init__(self, job_id = 0, job_num = 1, redo = False):
        super().__init__(job_id, job_num, redo)

    def getVideoAllInfo(self):
        output = {}
        for line in videos:
            video_url, video_author, video_title = line[:-1].split(',')
            num_frame = len(glob(Dv+video_url+'/frame/*.png'))
            video_sz, video_fps = getVideoInfo(Dv+video_url+'.mp4')
            output[video_url] = {'author': video_author,
                                 'title': video_title,
                                 'num_frame': num_frame,
                                 'fps': float(video_fps),
                                 'size': [int(x) for x in video_sz.split('x')]}
        json.dump(output, open(Dv+'data/video%s.json'%suf,'w'))

    def getVideoPath(self, output_folder = None):
        if output_folder is None:
            output_folder = self.video_data_folder 
        return output_folder + self.video_url + '.mp4'

    def getVideoMP4(self, video_url = None, output_file = None):
        if video_url is None:
            video_url = self.video_url
        if output_file is None:
            output_file = self.getVideoPath()

        vutil.downloadVideo(video_url, output_file)

    def getVideoFrames(self, ffmpeg, video_path = None, output_file = None):
        if video_path is None:
            video_path = self.getVideoPath()
        if output_file is None:
            output_file = self.getFrameName(-1)

        if not os.path.exists(output_file % (1)):
            vutil.mkdir(output_file, 1)
            os.system(ffmpeg + ' -i %s %s' % (video_path, output_file))

