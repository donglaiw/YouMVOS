from .control import videoDownloader
from .control import videoProcessor
from .control import videoProofreader
from .control import videoVisualizer
from .videoData import videoData
from . import videoUtil 

class videoTool(object):
    def __init__(self, job_id = 0, job_num = 1, redo = False):
        self.data = videoData(job_id, job_num) 
        self.proofreader = videoProofreader(self.data)
        self.processor = videoProcessor(self.data)
        self.downloader = videoDownloader(self.data)
        self.visualizer = videoVisualizer(self.data)
        self.util = videoUtil

    ####
    # Computation config
    def setSingleProcess(self):
        self.data.job_id = 0
        self.data.job_num = 1

    def setRedo(self, redo):
        self.data.redo = redo
