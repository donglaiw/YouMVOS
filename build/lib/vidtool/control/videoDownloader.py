import os
import json
from .. import videoUtil as vutil


class videoDownloader(object):
    def __init__(self, data = None):
        self.data = data

    def getVideoPath(self, output_folder = None):
        if output_folder is None:
            output_folder = self.data.video_download_folder 
        return output_folder + self.data.video_url + '.mp4'

    def downloadVideoMP4(self, video_url = None, output_file = None):
        if video_url is None:
            video_url = self.data.video_url
        if output_file is None:
            output_file = self.getVideoPath()

        vutil.downloadVideo(video_url, output_file)

    def extractVideoFrames(self, ffmpeg, video_path = None, output_file = None):
        if video_path is None:
            video_path = self.getVideoPath()
        if output_file is None:
            output_file = self.getFrameName(-1)

        if not os.path.exists(output_file % (1)):
            vutil.mkdir(output_file, 1)
            os.system(ffmpeg + ' -i %s %s' % (video_path, output_file))

