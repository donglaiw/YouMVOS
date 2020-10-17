import os
import json
from .. import videoUtil as vutil


class videoDownloader(object):
    def __init__(self, data = None):
        self.data = data

    def getVideoPath(self, output_folder = None):
        if output_folder is None:
            output_folder = self.data.FOLDER_DOWNLOAD + self.data.video_name + '/'
        return output_folder + self.data.video_url + '.mp4'

    def downloadVideoMP4(self, video_url = None, output_file = None):
        if video_url is None:
            video_url = self.data.video_url
        if output_file is None:
            output_file = self.getVideoPath()

        vutil.downloadVideo(video_url, output_file, 136)
        if not os.path.exists(output_file):
            print('try 480p')
            vutil.downloadVideo(video_url, output_file, 135)

    def extractVideoFrames(self, video_path = None, output_file = None):
        if video_path is None:
            video_path = self.getVideoPath()
        if output_file is None:
            output_file = self.data.getFrameName(-1)

        if not os.path.exists(output_file % (1)):
            vutil.mkdir(output_file, 'dir')
            os.system(self.data.LIB_FFMPEG + ' -i %s %s' % (video_path, output_file))

