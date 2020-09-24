from .control import videoDownloader
from .control import videoProcessor
from .control import videoProofreader
from .control import videoVisualizer
from .videoData import videoData
from . import videoUtil 

class videoTool(object):
    def __init__(self, job_id = 0, job_num = 1, redo = False):
        self.job_id = job_id
        self.job_num = job_num
        self.redo = redo
        self.data = videoData() 
        self.proofreader = videoProofreader(self.data)
        self.processor = videoProcessor(self.data)
        self.downloader = videoDownloader(self.data)
        self.visualizer = videoVisualizer(self.data)
        self.util = videoUtil

    ####
    # Computation config
    def setSingleProcess(self):
        self.job_id = 0
        self.job_num = 1

    def setRedo(self, redo):
        self.redo = redo


